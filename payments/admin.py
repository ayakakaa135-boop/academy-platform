from django.contrib import admin

# Register your models here.
from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Payment, Order


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'user',
        'course',
        'amount',
        'currency',
        'status',
        'created_at',
        'completed_at'
    ]
    list_filter = ['status', 'currency', 'created_at']
    search_fields = [
        'user__username',
        'user__email',
        'course__title',
        'stripe_payment_intent_id',
        'transaction_id'
    ]
    readonly_fields = [
        'id',
        'created_at',
        'updated_at',
        'completed_at',
        'stripe_payment_intent_id',
        'stripe_charge_id'
    ]

    fieldsets = (
        (_('معلومات أساسية'), {
            'fields': ('id', 'user', 'course')
        }),
        (_('تفاصيل الدفع'), {
            'fields': ('amount', 'currency', 'status', 'payment_method')
        }),
        (_('معلومات Stripe'), {
            'fields': ('stripe_payment_intent_id', 'stripe_charge_id', 'transaction_id')
        }),
        (_('التواريخ'), {
            'fields': ('created_at', 'updated_at', 'completed_at')
        }),
    )


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'user',
        'course',
        'total_amount',
        'status',
        'created_at',
        'completed_at'
    ]
    list_filter = ['status', 'created_at']
    search_fields = ['user__username', 'user__email', 'course__title']
    readonly_fields = ['id', 'created_at', 'updated_at', 'completed_at']

    fieldsets = (
        (_('معلومات أساسية'), {
            'fields': ('id', 'user', 'course', 'payment')
        }),
        (_('تفاصيل الطلب'), {
            'fields': ('total_amount', 'status')
        }),
        (_('التواريخ'), {
            'fields': ('created_at', 'updated_at', 'completed_at')
        }),
    )