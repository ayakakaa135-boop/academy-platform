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
            logger.error(f"Stripe error: {str(e)}")
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
    
    IMPORTANT: This view ONLY displays the success page.
    The actual enrollment activation is handled by the Webhook for security.
    
    This ensures that:
    - Users cannot manipulate URLs to gain access
    - Closing the browser doesn't affect enrollment
    - Payment verification happens server-side via Stripe
    """
    order_id = request.GET.get('order_id')
    session_id = request.GET.get('session_id')
    
    if not order_id:
        messages.warning(request, _('لم يتم العثور على معلومات الطلب'))
        return redirect('courses:home')

    try:
        order = get_object_or_404(Order, id=order_id, user=request.user)
    except:
        messages.error(request, _('طلب غير صالح'))
        return redirect('courses:home')
    
    # Check if enrollment exists (should be created by webhook)
    is_enrolled = Enrollment.objects.filter(
        user=request.user, 
        course=order.course, 
        is_active=True
    ).exists()
    
    # If webhook hasn't processed yet, show pending message
    if order.status == 'pending' and not is_enrolled:
        context = {
            'order': order,
            'course': order.course,
            'is_enrolled': False,
            'pending': True,
            'message': _('جاري معالجة طلبك... سيتم تفعيل الاشتراك خلال لحظات')
        }
        return render(request, 'payments/success.html', context)

    context = {
        'order': order,
        'course': order.course,
        'is_enrolled': is_enrolled,
        'pending': False,
    }
    return render(request, 'payments/success.html', context)


@csrf_exempt
def stripe_webhook(request):
    """
    Handle Stripe webhook events
    
    CRITICAL: This is where ALL enrollment activation happens.
    This ensures security and reliability regardless of user actions.
    """
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')

    # Verify webhook signature
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        logger.error(f"Invalid payload: {str(e)}")
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        logger.error(f"Invalid signature: {str(e)}")
        return HttpResponse(status=400)
    except Exception as e:
        logger.error(f"Unexpected webhook error: {str(e)}")
        return HttpResponse(status=400)

    # Handle the event
    event_type = event.get('type') if isinstance(event, dict) else event.type
    logger.info(f"Received Stripe event: {event_type}")
    
    if event_type == 'checkout.session.completed':
        session = event.get('data', {}).get('object') if isinstance(event, dict) else event.data.object
        logger.info(f"Processing checkout.session.completed")
        handle_checkout_session_completed(session)

    elif event_type == 'payment_intent.succeeded':
        payment_intent = event.get('data', {}).get('object') if isinstance(event, dict) else event.data.object
        handle_payment_intent_succeeded(payment_intent)

    elif event_type == 'payment_intent.payment_failed':
        payment_intent = event.get('data', {}).get('object') if isinstance(event, dict) else event.data.object
        handle_payment_intent_failed(payment_intent)

    return HttpResponse(status=200)


def handle_checkout_session_completed(session):
    """
    Handle completed checkout session
    
    THIS IS THE MAIN ENROLLMENT ACTIVATION POINT
    """
    try:
        # Get order_id from metadata
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
        
        # Verify payment status before activation
        payment_status = session.get('payment_status') if isinstance(session, dict) else getattr(session, 'payment_status', None)
        if payment_status != 'paid':
            logger.warning(f"Checkout session for order {order_id} not paid yet. Status: {payment_status}")
            return
            
        # Check if already processed to avoid duplicate activation
        if order.status == 'completed':
            logger.info(f"Order {order_id} already completed. Skipping.")
            return

        logger.info(f"Activating enrollment for order {order_id}")

        # 1. Update order status
        order.status = 'completed'
        order.completed_at = timezone.now()
        order.save()
        logger.info(f"Order {order_id} marked as completed")
        
        # 2. Update payment status
        order_payment = order.payment if order.payment_id else None
        if order_payment:
            order_payment.status = 'completed'
            order_payment.completed_at = timezone.now()
            # Update payment intent ID if it was missing
            payment_intent = session.get('payment_intent') if isinstance(session, dict) else getattr(session, 'payment_intent', None)
            if not order_payment.stripe_payment_intent_id and payment_intent:
                order_payment.stripe_payment_intent_id = payment_intent
            order_payment.save()
            logger.info(f"Payment updated for order {order_id}")
            
        # 3. CREATE OR ACTIVATE ENROLLMENT - THIS IS THE CRITICAL STEP
        enrollment, created = Enrollment.objects.get_or_create(
            user=order.user,
            course=order.course,
            defaults={'is_active': True}
        )
        
        if not created:
            # If enrollment exists but was inactive, activate it
            enrollment.is_active = True
            enrollment.save()
            logger.info(f"Existing enrollment reactivated for user {order.user.id} in course {order.course.id}")
        else:
            logger.info(f"New enrollment created for user {order.user.id} in course {order.course.id}")
        
        # 4. Send confirmation email (after successful enrollment)
        try:
            send_purchase_confirmation_email(order.user, order.course)
            logger.info(f"Confirmation email sent to {order.user.email}")
        except Exception as email_error:
            # Log but don't fail - enrollment is already active
            logger.error(f"Failed to send confirmation email: {str(email_error)}")
            
    except Exception as e:
        logger.error(f"Error handling checkout session: {str(e)}", exc_info=True)


def handle_payment_intent_succeeded(payment_intent):
    """
    Handle successful payment intent
    
    Backup activation point if checkout.session.completed is missed
    """
    try:
        pi_id = payment_intent.get('id') if isinstance(payment_intent, dict) else payment_intent.id
        payment = Payment.objects.filter(
            stripe_payment_intent_id=pi_id
        ).first()

        if not payment:
            logger.warning(f"No payment found for payment_intent {pi_id}")
            return

        # If payment is already completed, don't process again
        if payment.status == 'completed':
            logger.info(f"Payment {pi_id} already completed")
            return

        payment.status = 'completed'
        payment.completed_at = timezone.now()
        payment.save()
        logger.info(f"Payment {pi_id} marked as completed")
        
        # Also update order if linked
        if hasattr(payment, 'order'):
            order = payment.order
            if order.status != 'completed':
                order.status = 'completed'
                order.completed_at = timezone.now()
                order.save()
                
                # ACTIVATE ENROLLMENT
                enrollment, created = Enrollment.objects.get_or_create(
                    user=order.user,
                    course=order.course,
                    defaults={'is_active': True}
                )
                if not created:
                    enrollment.is_active = True
                    enrollment.save()
                
                logger.info(f"Enrollment activated via payment_intent for user {order.user.id}")
                
                # Send email
                try:
                    send_purchase_confirmation_email(order.user, order.course)
                except Exception as e:
                    logger.error(f"Failed to send email: {str(e)}")
                    
    except Exception as e:
        logger.error(f"Error handling payment intent: {str(e)}", exc_info=True)


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
            logger.info(f"Payment {pi_id} marked as failed")
            
            # Update order if exists
            if hasattr(payment, 'order'):
                order = payment.order
                order.status = 'failed'
                order.save()
                logger.info(f"Order {order.id} marked as failed")
                
    except Exception as e:
        logger.error(f"Error handling failed payment: {str(e)}", exc_info=True)


def send_purchase_confirmation_email(user, course):
    """Send email confirmation after successful purchase"""
    from django.template.loader import render_to_string
    from django.core.mail import EmailMultiAlternatives
    from django.utils.html import strip_tags

    subject = _('تأكيد شراء الدورة - {}').format(course.title)

    context = {
        'user': user,
        'course': course,
        'course_url': f"{settings.SITE_URL if hasattr(settings, 'SITE_URL') else 'http://localhost:8000'}{course.get_absolute_url()}",
        'site_url': settings.SITE_URL if hasattr(settings, 'SITE_URL') else 'http://localhost:8000',
        'purchase_date': timezone.now(),
        'order_id': timezone.now().strftime('%Y%m%d%H%M%S'),
    }

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


@login_required
def payment_history(request):
    """
    View payment history for current user
    Template: payments/history.html
    """
    payments = Payment.objects.filter(user=request.user).select_related('course').order_by('-created_at')
    orders = Order.objects.filter(user=request.user).select_related('course', 'payment').order_by('-created_at')

    context = {
        'payments': payments,
        'orders': orders,
    }
    return render(request, 'payments/history.html', context)
