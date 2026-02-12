from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.utils import timezone
from django.db import transaction
import stripe

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
                    '/payments/success/') + f'?session_id={{CHECKOUT_SESSION_ID}}&order_id={order.id}',
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
    Handle successful payment
    Template: payments/success.html
    """
    session_id = request.GET.get('session_id')
    order_id = request.GET.get('order_id')

    if not session_id or not order_id:
        messages.error(request, _('معلومات الدفع غير صحيحة'))
        return redirect('courses:home')

    order = get_object_or_404(Order, id=order_id, user=request.user)

    if order.status != 'completed':
        messages.info(request, _('تم استلام عملية الدفع وجاري تأكيدها. سيتم تفعيل الاشتراك تلقائياً.'))
        return redirect('courses:detail', slug=order.course.slug)

    context = {
        'order': order,
        'course': order.course,
    }
    return render(request, 'payments/success.html', context)


@csrf_exempt
def stripe_webhook(request):
    """
    Handle Stripe webhook events
    """
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError:
        return HttpResponse(status=400)

    # Handle the event
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        handle_checkout_session_completed(session)

    elif event['type'] == 'payment_intent.succeeded':
        payment_intent = event['data']['object']
        handle_payment_intent_succeeded(payment_intent)

    elif event['type'] == 'payment_intent.payment_failed':
        payment_intent = event['data']['object']
        handle_payment_intent_failed(payment_intent)

    return HttpResponse(status=200)


def handle_checkout_session_completed(session):
    """Handle completed checkout session"""
    try:
        order_id = session.metadata.get('order_id')
        if order_id:
            complete_order_from_session(order_id, session)
    except Exception as e:
        print(f"Error handling checkout session: {str(e)}")


@transaction.atomic
def complete_order_from_session(order_id, session):
    order = Order.objects.select_related('payment', 'course', 'user').get(id=order_id)
    payment = order.payment

    if payment:
        payment.status = 'completed'
        payment.completed_at = timezone.now()
        payment.stripe_charge_id = session.get('payment_intent', '')
        payment.stripe_payment_intent_id = session.get('payment_intent', '')
        payment.save()

    order.status = 'completed'
    order.completed_at = timezone.now()
    order.save()

    enrollment, created = Enrollment.objects.get_or_create(
        user=order.user,
        course=order.course,
        defaults={'is_active': True}
    )

    if not created and not enrollment.is_active:
        enrollment.is_active = True
        enrollment.save(update_fields=['is_active'])

    send_purchase_confirmation_email(order.user, order.course)


def handle_payment_intent_succeeded(payment_intent):
    """Handle successful payment intent"""
    try:
        payment = Payment.objects.filter(
            stripe_payment_intent_id=payment_intent.id
        ).first()

        if payment:
            payment.status = 'completed'
            payment.completed_at = timezone.now()
            payment.save()
    except Exception as e:
        print(f"Error handling payment intent: {str(e)}")


def handle_payment_intent_failed(payment_intent):
    """Handle failed payment intent"""
    try:
        payment = Payment.objects.filter(
            stripe_payment_intent_id=payment_intent.id
        ).first()

        if payment:
            payment.status = 'failed'
            payment.save()
    except Exception as e:
        print(f"Error handling failed payment: {str(e)}")


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
        print(f"Error sending purchase confirmation email: {e}")


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
