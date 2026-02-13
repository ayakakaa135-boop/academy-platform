from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from django.core.mail import send_mail
from django.db import transaction
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

            logger.info(f"Created order {order.id} for user {request.user.id}")

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
    
    SECURITY APPROACH:
    1. Webhook is PRIMARY - most secure
    2. This page is FALLBACK - with strong verification
    3. All actions are protected by Stripe verification
    """
    order_id = request.GET.get('order_id')
    session_id = request.GET.get('session_id')
    
    if not order_id:
        messages.warning(request, _('لم يتم العثور على معلومات الطلب'))
        return redirect('courses:home')

    # SECURITY: Verify order belongs to current user
    try:
        order = Order.objects.select_related('course', 'payment').get(
            id=order_id, 
            user=request.user  # Critical: Only allow access to own orders
        )
    except Order.DoesNotExist:
        logger.warning(f"Unauthorized order access attempt: user={request.user.id}, order={order_id}")
        messages.error(request, _('طلب غير صالح أو غير مصرح به'))
        return redirect('courses:home')
    
    logger.info(f"User {request.user.id} accessed success page for order {order.id}")
    
    # FALLBACK MECHANISM (only if webhook hasn't processed yet)
    # This is SECURE because:
    # 1. We verify with Stripe directly (not trusting URL params)
    # 2. We check metadata matches our order
    # 3. We verify payment_status is 'paid'
    if session_id and order.status != 'completed':
        logger.info(f"Order {order.id} still pending. Attempting SECURE fallback verification...")
        
        try:
            # SECURITY: Retrieve session directly from Stripe (not from user input)
            checkout_session = stripe.checkout.Session.retrieve(session_id)
            
            # Extract metadata safely
            session_metadata = checkout_session.get('metadata', {}) if isinstance(checkout_session, dict) else getattr(checkout_session, 'metadata', {})
            session_order_id = session_metadata.get('order_id')
            
            # SECURITY CHECKS:
            # 1. Payment must be confirmed by Stripe
            # 2. Order ID in Stripe must match our order
            # 3. User ID in Stripe must match current user
            session_user_id = session_metadata.get('user_id')
            
            payment_verified = (
                checkout_session.payment_status == 'paid' and
                str(session_order_id) == str(order.id) and
                str(session_user_id) == str(request.user.id)
            )
            
            if payment_verified:
                logger.info(f"✓ Payment verified for order {order.id}. Activating via fallback...")
                
                # Process the order (same as webhook)
                handle_checkout_session_completed(checkout_session)
                
                # Refresh from database
                order.refresh_from_db()
                logger.info(f"✓ Order {order.id} processed successfully via fallback")
            else:
                logger.warning(
                    f"Payment verification failed for order {order.id}: "
                    f"paid={checkout_session.payment_status}, "
                    f"order_match={str(session_order_id)==str(order.id)}, "
                    f"user_match={str(session_user_id)==str(request.user.id)}"
                )
                
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error during fallback: {str(e)}")
        except Exception as e:
            logger.error(f"Fallback verification error: {str(e)}")
    
    # Check enrollment status
    is_enrolled = Enrollment.objects.filter(
        user=request.user, 
        course=order.course, 
        is_active=True
    ).exists()
    
    # If still pending, show appropriate message
    if order.status == 'pending' and not is_enrolled:
        context = {
            'order': order,
            'course': order.course,
            'is_enrolled': False,
            'pending': True,
            'message': _('جاري معالجة الدفع... سيتم تفعيل الاشتراك خلال لحظات.')
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
    
    PRIMARY ENROLLMENT ACTIVATION POINT
    This is the most secure method as it comes directly from Stripe
    """
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')

    # Verify webhook signature (CRITICAL FOR SECURITY)
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
        logger.info("✓ Webhook signature verified")
    except ValueError as e:
        logger.error(f"Invalid webhook payload: {str(e)}")
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        logger.error(f"Invalid webhook signature: {str(e)}")
        return HttpResponse(status=400)
    except Exception as e:
        logger.error(f"Webhook error: {str(e)}")
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

    return HttpResponse(status=200)


def handle_checkout_session_completed(session):
    """
    Handle completed checkout session
    
    This function is called from:
    1. Webhook (primary, most secure)
    2. payment_success fallback (after Stripe verification)
    """
    try:
        # Get order_id from metadata
        metadata = session.get('metadata', {}) if isinstance(session, dict) else getattr(session, 'metadata', {})
        order_id = metadata.get('order_id')
        
        if not order_id:
            logger.error("No order_id in session metadata")
            return

        # Use transaction to ensure atomicity
        with transaction.atomic():
            try:
                # Lock the order row to prevent race conditions
                order = Order.objects.select_for_update().get(id=order_id)
            except Order.DoesNotExist:
                logger.error(f"Order {order_id} not found")
                return
            
            # Check if already processed (prevent duplicate processing)
            if order.status == 'completed':
                logger.info(f"Order {order_id} already completed. Skipping.")
                return
            
            logger.info(f"Processing order {order_id}...")
            
            # 1. Send confirmation email FIRST
            try:
                logger.info(f"Sending confirmation email to {order.user.email}")
                send_purchase_confirmation_email(order.user, order.course)
                logger.info("✓ Email sent")
            except Exception as email_error:
                logger.error(f"Failed to send email: {str(email_error)}")
                # Continue even if email fails
            
            # 2. Update order status
            order.status = 'completed'
            order.completed_at = timezone.now()
            order.save()
            logger.info(f"✓ Order {order_id} completed")
            
            # 3. Update payment status
            if order.payment:
                order.payment.status = 'completed'
                order.payment.completed_at = timezone.now()
                
                # Update payment intent ID if missing
                payment_intent = session.get('payment_intent') if isinstance(session, dict) else getattr(session, 'payment_intent', None)
                if not order.payment.stripe_payment_intent_id and payment_intent:
                    order.payment.stripe_payment_intent_id = payment_intent
                
                order.payment.save()
                logger.info(f"✓ Payment completed")
            
            # 4. CREATE OR ACTIVATE ENROLLMENT
            enrollment, created = Enrollment.objects.get_or_create(
                user=order.user,
                course=order.course,
                defaults={'is_active': True}
            )
            
            if not created:
                enrollment.is_active = True
                enrollment.save()
                logger.info(f"✓ Enrollment reactivated")
            else:
                logger.info(f"✓ Enrollment created")
            
            logger.info(f"✓✓✓ Order {order_id} fully processed. User {order.user.id} enrolled in course {order.course.id}")
            
    except Exception as e:
        logger.error(f"Error handling checkout session: {str(e)}", exc_info=True)


def handle_payment_intent_succeeded(payment_intent):
    """Handle successful payment intent (backup activation point)"""
    try:
        pi_id = payment_intent.get('id') if isinstance(payment_intent, dict) else payment_intent.id
        payment = Payment.objects.filter(stripe_payment_intent_id=pi_id).first()

        if not payment:
            logger.warning(f"No payment found for payment_intent {pi_id}")
            return

        if payment.status == 'completed':
            logger.info(f"Payment {pi_id} already completed")
            return

        payment.status = 'completed'
        payment.completed_at = timezone.now()
        payment.save()
        
        # Update order if linked
        if hasattr(payment, 'order'):
            order = payment.order
            if order.status != 'completed':
                # Send email
                try:
                    send_purchase_confirmation_email(order.user, order.course)
                except:
                    pass

                order.status = 'completed'
                order.completed_at = timezone.now()
                order.save()
                
                # Activate enrollment
                enrollment, created = Enrollment.objects.get_or_create(
                    user=order.user,
                    course=order.course,
                    defaults={'is_active': True}
                )
                if not created:
                    enrollment.is_active = True
                    enrollment.save()
                    
                logger.info(f"✓ Enrollment activated via payment_intent for order {order.id}")
                
    except Exception as e:
        logger.error(f"Error handling payment intent: {str(e)}", exc_info=True)


def handle_payment_intent_failed(payment_intent):
    """Handle failed payment intent"""
    try:
        pi_id = payment_intent.get('id') if isinstance(payment_intent, dict) else payment_intent.id
        payment = Payment.objects.filter(stripe_payment_intent_id=pi_id).first()

        if payment:
            payment.status = 'failed'
            payment.save()
            logger.info(f"Payment {pi_id} marked as failed")
            
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
    """View payment history for current user"""
    payments = Payment.objects.filter(user=request.user).select_related('course').order_by('-created_at')
    orders = Order.objects.filter(user=request.user).select_related('course', 'payment').order_by('-created_at')

    context = {
        'payments': payments,
        'orders': orders,
    }
    return render(request, 'payments/history.html', context)
