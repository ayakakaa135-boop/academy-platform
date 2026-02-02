from django.db import models

# Create your models here.
from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from courses.models import Course
import uuid


class Payment(models.Model):
    """
    Payment transaction model
    """
    PAYMENT_STATUS = [
        ('pending', _('قيد الانتظار')),
        ('completed', _('مكتمل')),
        ('failed', _('فشل')),
        ('refunded', _('مسترد')),
    ]

    # Payment info
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='payments',
        verbose_name=_('المستخدم')
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='payments',
        verbose_name=_('الدورة')
    )

    # Payment details
    amount = models.DecimalField(_('المبلغ'), max_digits=10, decimal_places=2)
    currency = models.CharField(_('العملة'), max_length=3, default='USD')
    status = models.CharField(
        _('الحالة'),
        max_length=20,
        choices=PAYMENT_STATUS,
        default='pending'
    )

    # Stripe info
    stripe_payment_intent_id = models.CharField(
        _('معرف Stripe'),
        max_length=255,
        blank=True
    )
    stripe_charge_id = models.CharField(
        _('معرف الدفع'),
        max_length=255,
        blank=True
    )

    # Metadata
    payment_method = models.CharField(_('طريقة الدفع'), max_length=50, blank=True)
    transaction_id = models.CharField(_('رقم المعاملة'), max_length=255, blank=True)

    # Timestamps
    created_at = models.DateTimeField(_('تاريخ الإنشاء'), auto_now_add=True)
    updated_at = models.DateTimeField(_('تاريخ التحديث'), auto_now=True)
    completed_at = models.DateTimeField(_('تاريخ الاكتمال'), null=True, blank=True)

    class Meta:
        verbose_name = _('دفعة')
        verbose_name_plural = _('الدفعات')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.course.title} - {self.amount} {self.currency}"


class Order(models.Model):
    """
    Order model for tracking course purchases
    """
    ORDER_STATUS = [
        ('pending', _('قيد الانتظار')),
        ('processing', _('قيد المعالجة')),
        ('completed', _('مكتمل')),
        ('cancelled', _('ملغي')),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='orders',
        verbose_name=_('المستخدم')
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='orders',
        verbose_name=_('الدورة')
    )
    payment = models.OneToOneField(
        Payment,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='order',
        verbose_name=_('الدفعة')
    )

    # Order details
    total_amount = models.DecimalField(_('المبلغ الإجمالي'), max_digits=10, decimal_places=2)
    status = models.CharField(
        _('الحالة'),
        max_length=20,
        choices=ORDER_STATUS,
        default='pending'
    )

    # Timestamps
    created_at = models.DateTimeField(_('تاريخ الإنشاء'), auto_now_add=True)
    updated_at = models.DateTimeField(_('تاريخ التحديث'), auto_now=True)
    completed_at = models.DateTimeField(_('تاريخ الاكتمال'), null=True, blank=True)

    class Meta:
        verbose_name = _('طلب')
        verbose_name_plural = _('الطلبات')
        ordering = ['-created_at']

    def __str__(self):
        return f"Order {self.id} - {self.user.username}"