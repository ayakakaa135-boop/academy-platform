"""
Models for courses app - Updated for django-modeltranslation
"""
from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from django.utils.text import slugify


class Category(models.Model):
    """
    Course category model
    """
    name = models.CharField(_('الاسم'), max_length=100)
    slug = models.SlugField(_('الرابط'), unique=True, blank=True)
    description = models.TextField(_('الوصف'), blank=True)
    created_at = models.DateTimeField(_('تاريخ الإنشاء'), auto_now_add=True)

    class Meta:
        verbose_name = _('فئة')
        verbose_name_plural = _('الفئات')
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            # استخدم النسخة الإنجليزية للـ slug
            from django.utils import translation
            with translation.override('en'):
                self.slug = slugify(str(self.name))
        super().save(*args, **kwargs)


class Course(models.Model):
    """
    Main course model
    """
    DIFFICULTY_CHOICES = [
        ('beginner', _('مبتدئ')),
        ('intermediate', _('متوسط')),
        ('advanced', _('متقدم')),
    ]

    title = models.CharField(_('العنوان'), max_length=200)
    slug = models.SlugField(_('الرابط'), unique=True, blank=True)
    description = models.TextField(_('الوصف'))
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        related_name='courses',
        verbose_name=_('الفئة')
    )
    instructor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='taught_courses',
        verbose_name=_('المدرس')
    )

    # Course details
    thumbnail = models.ImageField(_('صورة الدورة'), upload_to='courses/thumbnails/')
    price = models.DecimalField(_('السعر'), max_digits=10, decimal_places=2)
    difficulty = models.CharField(
        _('مستوى الصعوبة'),
        max_length=20,
        choices=DIFFICULTY_CHOICES,
        default='beginner'
    )
    duration_hours = models.PositiveIntegerField(_('مدة الدورة (بالساعات)'), default=0)

    # Course status
    is_published = models.BooleanField(_('منشورة'), default=False)
    is_featured = models.BooleanField(_('مميزة'), default=False)

    # Timestamps
    created_at = models.DateTimeField(_('تاريخ الإنشاء'), auto_now_add=True)
    updated_at = models.DateTimeField(_('تاريخ التحديث'), auto_now=True)

    class Meta:
        verbose_name = _('دورة')
        verbose_name_plural = _('الدورات')
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            from django.utils import translation
            with translation.override('en'):
                self.slug = slugify(str(self.title))
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('courses:detail', kwargs={'slug': self.slug})

    @property
    def total_lessons(self):
        return self.lessons.count()

    @property
    def total_students(self):
        return self.enrollments.filter(is_active=True).count()

    @property
    def average_rating(self):
        reviews = self.reviews.all()
        if reviews:
            return sum(r.rating for r in reviews) / len(reviews)
        return 0


class Lesson(models.Model):
    """
    Individual lesson within a course
    """
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='lessons',
        verbose_name=_('الدورة')
    )
    title = models.CharField(_('العنوان'), max_length=200)
    description = models.TextField(_('الوصف'), blank=True)
    video_url = models.URLField(_('رابط الفيديو'), blank=True)
    video_file = models.FileField(
        _('ملف الفيديو'),
        upload_to='courses/videos/',
        blank=True,
        null=True
    )
    duration_minutes = models.PositiveIntegerField(_('المدة (بالدقائق)'), default=0)
    order = models.PositiveIntegerField(_('الترتيب'), default=0)
    is_published = models.BooleanField(_('منشور'), default=True)
    is_preview = models.BooleanField(_('درس تجريبي'), default=False)

    created_at = models.DateTimeField(_('تاريخ الإنشاء'), auto_now_add=True)
    updated_at = models.DateTimeField(_('تاريخ التحديث'), auto_now=True)

    class Meta:
        verbose_name = _('درس')
        verbose_name_plural = _('الدروس')
        ordering = ['order', 'created_at']

    def __str__(self):
        return f"{self.course.title} - {self.title}"


class Enrollment(models.Model):
    """
    Student enrollment in a course
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='enrollments',
        verbose_name=_('المستخدم')
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='enrollments',
        verbose_name=_('الدورة')
    )
    enrolled_at = models.DateTimeField(_('تاريخ التسجيل'), auto_now_add=True)
    is_active = models.BooleanField(_('نشط'), default=True)
    progress = models.PositiveIntegerField(_('نسبة الإنجاز'), default=0)
    completed_at = models.DateTimeField(_('تاريخ الإكمال'), null=True, blank=True)

    class Meta:
        verbose_name = _('تسجيل')
        verbose_name_plural = _('التسجيلات')
        unique_together = ['user', 'course']
        ordering = ['-enrolled_at']

    def __str__(self):
        return f"{self.user.username} - {self.course.title}"


class Comment(models.Model):
    """
    Comments on course lessons
    """
    lesson = models.ForeignKey(
        Lesson,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name=_('الدرس')
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='lesson_comments',
        verbose_name=_('المستخدم')
    )
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='replies',
        verbose_name=_('رد على')
    )
    content = models.TextField(_('المحتوى'))
    created_at = models.DateTimeField(_('تاريخ الإنشاء'), auto_now_add=True)
    updated_at = models.DateTimeField(_('تاريخ التحديث'), auto_now=True)
    is_active = models.BooleanField(_('نشط'), default=True)

    class Meta:
        verbose_name = _('تعليق')
        verbose_name_plural = _('التعليقات')
        ordering = ['created_at']

    def __str__(self):
        return f"{self.user.username} - {self.lesson.title}"


class Review(models.Model):
    """
    Course reviews and ratings
    """
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name=_('الدورة')
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='course_reviews',
        verbose_name=_('المستخدم')
    )
    rating = models.PositiveIntegerField(_('التقييم'), choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField(_('التعليق'), blank=True)
    created_at = models.DateTimeField(_('تاريخ الإنشاء'), auto_now_add=True)
    updated_at = models.DateTimeField(_('تاريخ التحديث'), auto_now=True)

    class Meta:
        verbose_name = _('تقييم')
        verbose_name_plural = _('التقييمات')
        unique_together = ['course', 'user']
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.course.title} ({self.rating}★)"