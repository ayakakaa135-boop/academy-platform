from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse

from .models import Category, Course, Enrollment, Lesson


class HtmxLessonAccessTests(TestCase):
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
        category = Category.objects.create(name='Programming')
        self.course = Course.objects.create(
            title='Django Basics',
            description='Course description',
            category=category,
            instructor=self.instructor,
            thumbnail=SimpleUploadedFile('thumb.jpg', b'filecontent', content_type='image/jpeg'),
            price=Decimal('100.00'),
            is_published=True,
        )
        self.lesson = Lesson.objects.create(
            course=self.course,
            title='Lesson 1',
            description='Intro',
            order=1,
            is_preview=False,
        )

    def test_lesson_htmx_requires_enrollment_for_non_preview_lessons(self):
        self.client.login(username='student', password='pass12345')
        url = reverse('courses:lesson_htmx_content', kwargs={
            'course_slug': self.course.slug,
            'lesson_id': self.lesson.id,
        })

        response = self.client.get(url)

        self.assertEqual(response.status_code, 403)

    def test_lesson_htmx_returns_lessons_without_is_published_field(self):
        Enrollment.objects.create(user=self.student, course=self.course, is_active=True)
        self.client.login(username='student', password='pass12345')
        url = reverse('courses:lesson_htmx_content', kwargs={
            'course_slug': self.course.slug,
            'lesson_id': self.lesson.id,
        })

        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.lesson.title)

    def test_lesson_htmx_requires_login(self):
        url = reverse('courses:lesson_htmx_content', kwargs={
            'course_slug': self.course.slug,
            'lesson_id': self.lesson.id,
        })

        response = self.client.get(url)

        self.assertEqual(response.status_code, 403)

    def test_load_more_comments_requires_login(self):
        url = reverse('courses:load_more_comments', kwargs={'lesson_id': self.lesson.id})

        response = self.client.get(url)

        self.assertEqual(response.status_code, 403)
