from django.db import models

# Create your models here.
from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from django.utils.text import slugify
from tinymce.models import HTMLField


class BlogCategory(models.Model):
    """
    Blog post category
    """
    name = models.CharField(_('الاسم'), max_length=100)

    slug = models.SlugField(_('الرابط'), unique=True, blank=True)
    description = models.TextField(_('الوصف'), blank=True)

    class Meta:
        verbose_name = _('فئة المدونة')
        verbose_name_plural = _('فئات المدونة')
        ordering = ['name']

    def __str__(self):
        return self.name




class Post(models.Model):
    """
    Blog post model
    """
    STATUS_CHOICES = [
        ('draft', _('مسودة')),
        ('published', _('منشور')),
    ]

    title = models.CharField(_('العنوان'), max_length=200)
    slug = models.SlugField(_('الرابط'), unique=True, blank=True)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='blog_posts',
        verbose_name=_('الكاتب')
    )
    category = models.ForeignKey(
        BlogCategory,
        on_delete=models.SET_NULL,
        null=True,
        related_name='posts',
        verbose_name=_('الفئة')
    )

    # Content
    excerpt = models.TextField(_('ملخص'), max_length=300)

    content = HTMLField(_('المحتوى'))

    # Media
    featured_image = models.ImageField(
        _('الصورة المميزة'),
        upload_to='blog/images/',
        blank=True,
        null=True
    )

    # Metadata
    status = models.CharField(
        _('الحالة'),
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft'
    )
    is_featured = models.BooleanField(_('مميز'), default=False)
    views_count = models.PositiveIntegerField(_('عدد المشاهدات'), default=0)

    # SEO
    meta_description = models.CharField(_('وصف ميتا'), max_length=160, blank=True)
    meta_keywords = models.CharField(_('كلمات مفتاحية'), max_length=255, blank=True)

    # Timestamps
    created_at = models.DateTimeField(_('تاريخ الإنشاء'), auto_now_add=True)
    updated_at = models.DateTimeField(_('تاريخ التحديث'), auto_now=True)
    published_at = models.DateTimeField(_('تاريخ النشر'), null=True, blank=True)

    class Meta:
        verbose_name = _('مقالة')
        verbose_name_plural = _('المقالات')
        ordering = ['-published_at', '-created_at']

    def __str__(self):
        return self.title


    def get_absolute_url(self):
        return reverse('blog:detail', kwargs={'slug': self.slug})


class PostComment(models.Model):
    """
    Comments on blog posts
    """
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name=_('المقالة')
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='blog_comments',
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
    is_approved = models.BooleanField(_('موافق عليه'), default=True)
    created_at = models.DateTimeField(_('تاريخ الإنشاء'), auto_now_add=True)
    updated_at = models.DateTimeField(_('تاريخ التحديث'), auto_now=True)

    class Meta:
        verbose_name = _('تعليق')
        verbose_name_plural = _('التعليقات')
        ordering = ['created_at']

    def __str__(self):
        return f"{self.user.username} - {self.post.title}"