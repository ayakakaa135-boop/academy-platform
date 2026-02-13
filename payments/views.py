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

            logger.info(f"Created order {order.id} for user {request.user.id}, course {course.id}")

            # Create Stripe checkout session
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': 'usd',
                        'unit_amount': int(course.price * 100),
                        'product_data': {
                            'name': course.title,
                            'description': course.description[:100] if course.description else course.title,
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
                    'user_id': str(request.user.id),
                    'course_id': str(course.id),
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

            logger.info(f"Created payment {payment.id} for order {order.id}")
            logger.info(f"Redirecting to Stripe checkout: {checkout_session.url}")

            return redirect(checkout_session.url)

        except Exception as e:
            messages.error(request, _('حدث خطأ أثناء معالجة الدفع. يرجى المحاولة مرة أخرى.'))
            logger.error(f"Stripe checkout error: {str(e)}", exc_info=True)
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
    
    PRIMARY: Display success page
    FALLBACK: If webhook hasn't processed yet, verify and activate enrollment
    
    This dual approach ensures:
    1. Webhook is the main activation method (secure)
    2. Fallback prevents stuck orders if webhook is delayed/misconfigured
    """
    order_id = request.GET.get('order_id')
    session_id = request.GET.get('session_id')
    
    logger.info(f"Payment success page accessed. Order: {order_id}, Session: {session_id}")
    
    if not order_id:
        messages.warning(request, _('لم يتم العثور على معلومات الطلب'))
        return redirect('courses:home')

    try:
        order = get_object_or_404(Order, id=order_id, user=request.user)
    except Exception as e:
        logger.error(f"Invalid order {order_id}: {str(e)}")
        messages.error(request, _('طلب غير صالح'))
        return redirect('courses:home')
    
    logger.info(f"Order {order_id} found. Status: {order.status}")
    
    # FALLBACK MECHANISM: If order is still pending, verify with Stripe directly
    if session_id and order.status == 'pending':
        logger.warning(f"Order {order_id} still pending. Attempting fallback activation...")
        
        try:
            # Retrieve session from Stripe to verify payment
            session = stripe.checkout.Session.retrieve(session_id)
            
            logger.info(f"Stripe session retrieved. Payment status: {session.payment_status}")
            
            # Verify this is the correct session
            session_metadata = getattr(session, 'metadata', {})
            session_order_id = session_metadata.get('order_id')
            
            if str(session_order_id) != str(order.id):
                logger.error(f"Session order_id mismatch: {session_order_id} != {order.id}")
            elif session.payment_status == 'paid':
                logger.warning(f"FALLBACK ACTIVATION triggered for order {order_id}")
                
                # Activate enrollment using the same logic as webhook
                activate_enrollment(order, session)
                
                # Refresh order from database
                order.refresh_from_db()
                logger.info(f"Order {order_id} status after fallback: {order.status}")
                
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error during fallback verification: {str(e)}")
        except Exception as e:
            logger.error(f"Fallback activation failed: {str(e)}", exc_info=True)
    
    # Check enrollment status
    is_enrolled = Enrollment.objects.filter(
        user=request.user, 
        course=order.course, 
        is_active=True
    ).exists()
    
    logger.info(f"Enrollment status for user {request.user.id} in course {order.course.id}: {is_enrolled}")
    
    # If still pending after all checks
    if order.status == 'pending' and not is_enrolled:
        context = {
            'order': order,
            'course': order.course,
            'is_enrolled': False,
            'pending': True,
            'message': _('جاري معالجة طلبك... سيتم تفعيل الاشتراك خلال لحظات. إذا لم يتم التفعيل خلال دقيقة، يرجى التواصل مع الدعم الفني.')
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
    
    CRITICAL: This is the PRIMARY enrollment activation point.
    """
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    
    logger.info("Webhook received from Stripe")

    # Verify webhook signature
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
        logger.info("Webhook signature verified successfully")
    except ValueError as e:
        logger.error(f"Invalid webhook payload: {str(e)}")
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        logger.error(f"Invalid webhook signature: {str(e)}")
        return HttpResponse(status=400)
    except Exception as e:
        logger.error(f"Unexpected webhook error: {str(e)}", exc_info=True)
        return HttpResponse(status=400)

    # Handle the event
    event_type = event.get('type') if isinstance(event, dict) else event.type
    logger.info(f"Processing webhook event: {event_type}")
    
    if event_type == 'checkout.session.completed':
        session = event.get('data', {}).get('object') if isinstance(event, dict) else event.data.object
        handle_checkout_session_completed(session)

    elif event_type == 'payment_intent.succeeded':
        payment_intent = event.get('data', {}).get('object') if isinstance(event, dict) else event.data.object
        handle_payment_intent_succeeded(payment_intent)

    elif event_type == 'payment_intent.payment_failed':
        payment_intent = event.get('data', {}).get('object') if isinstance(event, dict) else event.data.object
        handle_payment_intent_failed(payment_intent)
    
    else:
        logger.info(f"Unhandled event type: {event_type}")

    return HttpResponse(status=200)


def activate_enrollment(order, session=None):
    """
    Central function to activate enrollment for an order.
    Can be called from webhook or fallback mechanism.
    
    Args:
        order: Order object
        session: Stripe session object (optional, for payment intent ID)
    """
    try:
        # Check if already processed
        if order.status == 'completed':
            logger.info(f"Order {order.id} already completed. Skipping activation.")
            return True
        
        logger.info(f"Activating enrollment for order {order.id}")
        
        # 1. Update order status
        order.status = 'completed'
        order.completed_at = timezone.now()
        order.save()
        logger.info(f"✓ Order {order.id} marked as completed")
        
        # 2. Update payment status
        if order.payment:
            order.payment.status = 'completed'
            order.payment.completed_at = timezone.now()
            
            # Update payment intent ID if available and missing
            if session:
                payment_intent = session.get('payment_intent') if isinstance(session, dict) else getattr(session, 'payment_intent', None)
                if payment_intent and not order.payment.stripe_payment_intent_id:
                    order.payment.stripe_payment_intent_id = payment_intent
            
            order.payment.save()
            logger.info(f"✓ Payment {order.payment.id} marked as completed")
        
        # 3. CREATE OR ACTIVATE ENROLLMENT
        enrollment, created = Enrollment.objects.get_or_create(
            user=order.user,
            course=order.course,
            defaults={'is_active': True}
        )
        
        if not created:
            enrollment.is_active = True
            enrollment.save()
            logger.info(f"✓ Existing enrollment reactivated for user {order.user.id} in course {order.course.id}")
        else:
            logger.info(f"✓ NEW enrollment created for user {order.user.id} in course {order.course.id}")
        
        # Verify enrollment was created
        enrollment_exists = Enrollment.objects.filter(
            user=order.user,
            course=order.course,
            is_active=True
        ).exists()
        
        if not enrollment_exists:
            logger.error(f"✗ CRITICAL: Enrollment was not created for order {order.id}")
            return False
        
        logger.info(f"✓ Enrollment verified: user {order.user.id} is now enrolled in course {order.course.id}")
        
        # 4. Send confirmation email
        try:
            send_purchase_confirmation_email(order.user, order.course)
            logger.info(f"✓ Confirmation email sent to {order.user.email}")
        except Exception as email_error:
            # Don't fail the whole process if email fails
            logger.error(f"✗ Failed to send confirmation email: {str(email_error)}")
        
        return True
        
    except Exception as e:
        logger.error(f"✗ Error activating enrollment for order {order.id}: {str(e)}", exc_info=True)
        return False


def handle_checkout_session_completed(session):
    """
    Handle completed checkout session from webhook
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
        
        # Verify payment status
        payment_status = session.get('payment_status') if isinstance(session, dict) else getattr(session, 'payment_status', None)
        if payment_status != 'paid':
            logger.warning(f"Checkout session for order {order_id} not paid yet. Status: {payment_status}")
            return
        
        logger.info(f"Checkout session completed for order {order_id}. Activating enrollment...")
        
        # Activate enrollment
        success = activate_enrollment(order, session)
        
        if success:
            logger.info(f"✓✓✓ Enrollment activation completed successfully for order {order_id}")
        else:
            logger.error(f"✗✗✗ Enrollment activation failed for order {order_id}")
            
    except Exception as e:
        logger.error(f"Error handling checkout session: {str(e)}", exc_info=True)


def handle_payment_intent_succeeded(payment_intent):
    """
    Handle successful payment intent from webhook
    Backup activation point if checkout.session.completed is missed
    """
    try:
        pi_id = payment_intent.get('id') if isinstance(payment_intent, dict) else payment_intent.id
        logger.info(f"Processing payment_intent.succeeded: {pi_id}")
        
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
        
        # Update order if linked
        if hasattr(payment, 'order'):
            order = payment.order
            if order.status != 'completed':
                logger.info(f"Activating enrollment via payment_intent for order {order.id}")
                activate_enrollment(order)
                
    except Exception as e:
        logger.error(f"Error handling payment intent: {str(e)}", exc_info=True)


def handle_payment_intent_failed(payment_intent):
    """Handle failed payment intent"""
    try:
        pi_id = payment_intent.get('id') if isinstance(payment_intent, dict) else payment_intent.id
        logger.info(f"Processing payment_intent.payment_failed: {pi_id}")
        
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
        'course_url': f"{getattr(settings, 'SITE_URL', 'http://localhost:8000')}{course.get_absolute_url()}",
        'site_url': getattr(settings, 'SITE_URL', 'http://localhost:8000'),
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
