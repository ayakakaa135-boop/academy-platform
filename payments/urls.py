from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('checkout/<slug:course_slug>/', views.create_checkout_session, name='checkout'),
    path('success/', views.payment_success, name='success'),
    # Webhook is now handled in urls_webhook.py outside i18n_patterns
    path('history/', views.payment_history, name='history'),
]
