from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from django.core.mail import send_mail
import stripe
import json
import logging

logger = logging.getLogger(__name__)

from courses.models import Course, Enrollment
from .models import Payment, Order

# Configure Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY


@login_required
def create_checkout_session(request, course_slug):
    """
    Create Stripe checkout session for course purchase
    Template: payments/checkout.html
    """
    course = get_object_or_404(Course, slug=course_slug, is_published=True)

    # Check if already enrolled
    if Enrollment.objects.filter(user=request.user, course=course, is_active=True).exists():
        messages.info(request, _('أنت مسجل بالفعل في هذه الدورة'))
        return redirect('courses:detail', slug=course_slug)

    if request.method == 'POST':
        try:
            # Create order
            order = Order.objects.create(
                user=request.user,
                course=course,
                total_amount=course.price,
                status='pending'
            )

            # Create Stripe checkout session
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': 'usd',
                        'unit_amount': int(course.price * 100),
                        'product_data': {
                            'name': course.title,
                            'description': course.description[:100],
                            'images': [request.build_absolute_uri(course.thumbnail.url)] if course.thumbnail else [],
                        },
                    },
                    'quantity': 1,
                }],
                mode='payment',
                success_url=request.build_absolute_uri(
                     '/payments/success/') + f'?order_id={order.id}&session_id={{CHECKOUT_SESSION_ID}}',
                cancel_url=request.build_absolute_uri(f'/course/{course.slug}/'),
                customer_email=request.user.email,
                metadata={
                    'user_id': request.user.id,
                    'course_id': course.id,
                    'order_id': str(order.id),
                }
            )

            # Create payment record
            payment = Payment.objects.create(
                user=request.user,
                course=course,
                amount=course.price,
                currency='USD',
                status='pending',
                stripe_payment_intent_id=checkout_session.payment_intent if checkout_session.payment_intent else '',
            )

            order.payment = payment
            order.save()

            return redirect(checkout_session.url)

        except Exception as e:
            messages.error(request, _('حدث خطأ أثناء معالجة الدفع. يرجى المحاولة مرة أخرى.'))
            print(f"Stripe error: {str(e)}")
            return redirect('courses:detail', slug=course_slug)

    context = {
        'course': course,
        'stripe_public_key': settings.STRIPE_PUBLIC_KEY,
    }
    return render(request, 'payments/checkout.html', context)


@login_required
def payment_success(request):
    """
    Handle successful payment redirection.
    The actual enrollment is handled by the Webhook for security.
    This view just shows the success page.
    """
    order_id = request.GET.get('order_id')
  
    if not order_id:
        return redirect('courses:home')

    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    # Check if enrollment exists (it might have been created by webhook already)
    is_enrolled = Enrollment.objects.filter(
        user=request.user, 
        course=order.course, 
        is_active=True
    ).exists()

    context = {
        'order': order,
        'course': order.course,
        'is_enrolled': is_enrolled,
    }
    return render(request, 'payments/success.html', context)


@csrf_exempt
def stripe_webhook(request):
    """
    Handle Stripe webhook events
    """
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')

   
   
       # Strictly validate webhook signature before processing any event.
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except (ValueError, stripe.error.SignatureVerificationError) as e:
        logger.warning(f"Webhook signature verification failed: {str(e)}")
        return HttpResponse(status=400)
    except Exception as e:
        logger.error(f"Unexpected Webhook error: {str(e)}")
        return HttpResponse(status=400)

    # Handle the event
    event_type = event.type
    logger.info(f"Received Stripe event: {event_type}")
    
    if event_type == 'checkout.session.completed':
        session = event.data.object
        logger.info(f"Processing checkout.session.completed")
        handle_checkout_session_completed(session)

    elif event_type == 'payment_intent.succeeded':
        payment_intent = event.data.object
        handle_payment_intent_succeeded(payment_intent)

    elif event_type == 'payment_intent.payment_failed':
        payment_intent = event.data.object
        handle_payment_intent_failed(payment_intent)

    return HttpResponse(status=200)


def handle_checkout_session_completed(session):
    """Handle completed checkout session"""
    try:
        # Try to get order_id from metadata
        metadata = session.get('metadata', {}) if isinstance(session, dict) else getattr(session, 'metadata', {})
        order_id = metadata.get('order_id')
        
        if not order_id:
            logger.error("No order_id found in session metadata")
            return

        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            logger.error(f"Order with ID {order_id} not found")
            return
            
        # 1. First, try to send the confirmation email as per site design
        # This is the "trigger" for the rest of the process
        email_sent = False
        try:
            logger.info(f"Attempting to send confirmation email to {order.user.email} for course {order.course.title}")
            send_purchase_confirmation_email(order.user, order.course)
            email_sent = True
            logger.info("Confirmation email sent successfully")
        except Exception as email_error:
            logger.error(f"CRITICAL: Failed to send confirmation email: {str(email_error)}")
            # We will still proceed to activate the course if email fails, 
            # but we log it as a critical error because the user expects the email.
            # In a production environment, you might want to retry this.

        # 2. Update order and payment status
        order.status = 'completed'
        order.completed_at = timezone.now()
        order.save()
        
        order_payment = order.payment if order.payment_id else None
        if order_payment:
            order_payment.status = 'completed'
            order_payment.completed_at = timezone.now()
            # Update payment intent ID if it was missing
            payment_intent = session.get('payment_intent') if isinstance(session, dict) else getattr(session, 'payment_intent', None)
            if not order_payment.stripe_payment_intent_id and payment_intent:
                order_payment.stripe_payment_intent_id = payment_intent
            order_payment.save()
            
        # 3. Create or activate enrollment (Open the course)
        enrollment, created = Enrollment.objects.get_or_create(
            user=order.user,
            course=order.course,
            defaults={'is_active': True}
        )
        if not created:
            enrollment.is_active = True
            enrollment.save()
        
        logger.info(f"Enrollment activated for user {order.user.id} in course {order.course.id}")
            
    except Exception as e:
        logger.error(f"Error handling checkout session: {str(e)}")


def handle_payment_intent_succeeded(payment_intent):
    """Handle successful payment intent"""
    try:
        pi_id = payment_intent.get('id') if isinstance(payment_intent, dict) else payment_intent.id
        payment = Payment.objects.filter(
            stripe_payment_intent_id=pi_id
        ).first()

        if payment:
            # If payment is already completed, don't do anything
            if payment.status == 'completed':
                return

            payment.status = 'completed'
            payment.completed_at = timezone.now()
            payment.save()
            
            # Also update order if linked
            if hasattr(payment, 'order'):
                order = payment.order
                if order.status != 'completed':
                    # Try to send email here too if it wasn't sent by checkout.session.completed
                    try:
                        send_purchase_confirmation_email(order.user, order.course)
                    except:
                        pass

                    order.status = 'completed'
                    order.completed_at = timezone.now()
                    order.save()
                    
                    # Ensure enrollment
                    enrollment, created = Enrollment.objects.get_or_create(
                        user=order.user,
                        course=order.course,
                        defaults={'is_active': True}
                    )
                    if not created:
                        enrollment.is_active = True
                        enrollment.save()
    except Exception as e:
        logger.error(f"Error handling payment intent: {str(e)}")


def handle_payment_intent_failed(payment_intent):
    """Handle failed payment intent"""
    try:
        pi_id = payment_intent.get('id') if isinstance(payment_intent, dict) else payment_intent.id
        payment = Payment.objects.filter(
            stripe_payment_intent_id=pi_id
        ).first()

        if payment:
            payment.status = 'failed'
            payment.save()
    except Exception as e:
        logger.error(f"Error handling failed payment: {str(e)}")


def send_purchase_confirmation_email(user, course):
    """Send email confirmation after successful purchase"""
    from django.template.loader import render_to_string
    from django.core.mail import EmailMultiAlternatives
    from django.utils.html import strip_tags
    from django.utils import timezone

    subject = _('تأكيد شراء الدورة - {}').format(course.title)

    context = {
        'user': user,
        'course': course,
        'course_url': f"{settings.SITE_URL if hasattr(settings, 'SITE_URL') else 'http://localhost:8000'}{course.get_absolute_url()}",
        'site_url': settings.SITE_URL if hasattr(settings, 'SITE_URL') else 'http://localhost:8000',
        'purchase_date': timezone.now(),
        'order_id': timezone.now().strftime('%Y%m%d%H%M%S'),
    }

    try:
        html_content = render_to_string('emails/course_purchase.html', context)
        text_content = strip_tags(html_content)

        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[user.email]
        )
        email.attach_alternative(html_content, "text/html")
        email.send()
    except Exception as e:
        logger.error(f"Error sending purchase confirmation email: {e}")
        # Re-raise to be caught by the caller
        raise


@login_required
def payment_history(request):
    """
    View payment history for current user
    Template: payments/history.html
    """
    payments = Payment.objects.filter(user=request.user).select_related('course')
    orders = Order.objects.filter(user=request.user).select_related('course', 'payment')

    context = {
        'payments': payments,
        'orders': orders,
    }
    return render(request, 'payments/history.html', context)
