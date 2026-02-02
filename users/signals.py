from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail, EmailMultiAlternatives
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.utils import timezone
from allauth.account.signals import user_signed_up, user_logged_in, password_changed
from .models import CustomUser


def send_html_email(subject, html_template, context, recipient_list):
    """
    Helper function to send HTML emails
    """
    try:
        html_content = render_to_string(html_template, context)
        text_content = strip_tags(html_content)

        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=recipient_list
        )
        email.attach_alternative(html_content, "text/html")
        email.send()
    except Exception as e:
        print(f"Error sending email: {e}")


@receiver(user_signed_up)
def send_welcome_email(request, user, **kwargs):
    """
    Send welcome email when user signs up (after email confirmation)
    """
    subject = _('مرحباً بك في الأكاديمية!')

    context = {
        'user': user,
        'site_url': settings.SITE_URL if hasattr(settings, 'SITE_URL') else 'http://localhost:8000',
    }

    send_html_email(
        subject=subject,
        html_template='emails/welcome_email.html',
        context=context,
        recipient_list=[user.email]
    )


@receiver(user_logged_in)
def send_login_notification(request, user, **kwargs):
    """
    Send email notification when user logs in
    """
    subject = _('تسجيل دخول جديد إلى حسابك')

    context = {
        'user': user,
        'login_time': timezone.now(),
        'password_reset_url': f"{settings.SITE_URL if hasattr(settings, 'SITE_URL') else 'http://localhost:8000'}/accounts/password/reset/",
    }

    send_html_email(
        subject=subject,
        html_template='emails/login_notification.html',
        context=context,
        recipient_list=[user.email]
    )


@receiver(password_changed)
def send_password_changed_email(request, user, **kwargs):
    """
    Send email notification when password is changed
    """
    subject = _('تم تغيير كلمة المرور بنجاح')

    context = {
        'user': user,
        'changed_time': timezone.now(),
        'login_url': f"{settings.SITE_URL if hasattr(settings, 'SITE_URL') else 'http://localhost:8000'}/accounts/login/",
    }

    send_html_email(
        subject=subject,
        html_template='emails/password_changed.html',
        context=context,
        recipient_list=[user.email]
    )