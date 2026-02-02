from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class CustomUser(AbstractUser):
    """
    Custom user model extending Django's AbstractUser
    """
    email = models.EmailField(_('البريد الإلكتروني'), unique=True)
    phone = models.CharField(_('رقم الهاتف'), max_length=20, blank=True)
    bio = models.TextField(_('نبذة عني'), blank=True)
    avatar = models.ImageField(
        _('الصورة الشخصية'),
        upload_to='avatars/',
        blank=True,
        null=True
    )
    date_of_birth = models.DateField(_('تاريخ الميلاد'), blank=True, null=True)

    # Enrollment tracking
    enrolled_courses = models.ManyToManyField(
        'courses.Course',
        through='courses.Enrollment',
        related_name='enrolled_users',
        verbose_name=_('الدورات المسجلة')
    )

    created_at = models.DateTimeField(_('تاريخ الإنشاء'), auto_now_add=True)
    updated_at = models.DateTimeField(_('تاريخ التحديث'), auto_now=True)

    class Meta:
        verbose_name = _('مستخدم')
        verbose_name_plural = _('المستخدمون')
        ordering = ['-created_at']

    def __str__(self):
        return self.username

    def get_full_name(self):
        """Return the full name of the user"""
        full_name = f"{self.first_name} {self.last_name}".strip()
        return full_name or self.username

    @property
    def is_instructor(self):
        """Check if user is an instructor"""
        return self.groups.filter(name='Instructors').exists() or self.is_staff