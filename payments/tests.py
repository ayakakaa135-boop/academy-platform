from decimal import Decimal
from django.contrib.auth import get_user_model
from django.core import mail
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse
from unittest.mock import patch

from courses.models import Category, Course, Enrollment
from payments.models import Order, Payment
from payments.views import complete_order_from_session


@override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
class PaymentWebhookTests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.student = user_model.objects.create_user(
            username='student',
            email='student@example.com',
            password='pass12345'
        )
        self.instructor = user_model.objects.create_user(
            username='teacher',
            email='teacher@example.com',
            password='pass12345'
        )
        self.category = Category.objects.create(name='Programming')
        self.course = Course.objects.create(
            title='Django Basics',
            description='Course description',
            category=self.category,
            instructor=self.instructor,
            thumbnail=SimpleUploadedFile('thumb.jpg', b'filecontent', content_type='image/jpeg'),
            price=Decimal('100.00'),
            is_published=True,
        )
        self.payment = Payment.objects.create(
            user=self.student,
            course=self.course,
            amount=Decimal('100.00'),
            status='pending',
            currency='USD',
        )
        self.order = Order.objects.create(
            user=self.student,
            course=self.course,
            payment=self.payment,
            total_amount=Decimal('100.00'),
            status='pending',
        )

    def test_complete_order_from_session_activates_enrollment_and_order(self):
        session = {
            'payment_intent': 'pi_test_123',
        }

        complete_order_from_session(str(self.order.id), session)

        self.order.refresh_from_db()
        self.payment.refresh_from_db()
        enrollment = Enrollment.objects.get(user=self.student, course=self.course)

        self.assertEqual(self.order.status, 'completed')
        self.assertEqual(self.payment.status, 'completed')
        self.assertEqual(self.payment.stripe_charge_id, 'pi_test_123')
        self.assertTrue(enrollment.is_active)
        self.assertEqual(len(mail.outbox), 1)

    def test_complete_order_from_session_is_idempotent(self):
        session = {
            'payment_intent': 'pi_test_123',
        }

        complete_order_from_session(str(self.order.id), session)
        complete_order_from_session(str(self.order.id), session)

        self.order.refresh_from_db()
        self.payment.refresh_from_db()

        self.assertEqual(self.order.status, 'completed')
        self.assertEqual(self.payment.status, 'completed')
        self.assertEqual(len(mail.outbox), 1)

    @override_settings(DEBUG=True)
    @patch('payments.views.stripe.checkout.Session.retrieve')
    def test_payment_success_allows_debug_fallback_without_webhook(self, mock_retrieve):
        mock_retrieve.return_value = type('Session', (), {'payment_status': 'paid', 'payment_intent': 'pi_test_123'})()
        self.client.login(username='student', password='pass12345')

        response = self.client.get(
            reverse('payments:success'),
            {'session_id': 'cs_test_123', 'order_id': str(self.order.id)}
        )

        self.order.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.order.status, 'completed')
