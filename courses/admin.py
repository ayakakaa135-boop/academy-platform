from django.contrib import admin

# Register your models here.
from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Category, Course, Lesson, Enrollment, Comment, Review


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'name_en', 'slug', 'created_at']
    search_fields = ['name', 'name_en']
    prepopulated_fields = {'slug': ('name_en',)}


class LessonInline(admin.TabularInline):
    model = Lesson
    extra = 1
    fields = ['title', 'title_en', 'order', 'duration_minutes', 'is_preview']


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = [
        'title',
        'category',
        'instructor',
        'price',
        'difficulty',
        'is_published',
        'is_featured',
        'created_at'
    ]
    list_filter = ['category', 'difficulty', 'is_published', 'is_featured', 'created_at']
    search_fields = ['title', 'title_en', 'description']
    prepopulated_fields = {'slug': ('title_en',)}
    inlines = [LessonInline]
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        (_('معلومات أساسية'), {
            'fields': ('title', 'title_en', 'slug', 'category', 'instructor')
        }),
        (_('الوصف'), {
            'fields': ('description', 'description_en')
        }),
        (_('تفاصيل الدورة'), {
            'fields': ('thumbnail', 'price', 'difficulty', 'duration_hours')
        }),
        (_('الحالة'), {
            'fields': ('is_published', 'is_featured')
        }),
        (_('التواريخ'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ['title', 'course', 'order', 'duration_minutes', 'is_preview', 'created_at']
    list_filter = ['course', 'is_preview', 'created_at']
    search_fields = ['title', 'title_en', 'course__title']
    ordering = ['course', 'order']


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ['user', 'course', 'enrolled_at', 'progress', 'is_active', 'completed_at']
    list_filter = ['is_active', 'enrolled_at', 'course']
    search_fields = ['user__username', 'user__email', 'course__title']
    readonly_fields = ['enrolled_at']


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['user', 'lesson', 'content_preview', 'parent', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['user__username', 'lesson__title', 'content']
    readonly_fields = ['created_at', 'updated_at']

    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content

    content_preview.short_description = _('المحتوى')


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['user', 'course', 'rating', 'comment_preview', 'created_at']
    list_filter = ['rating', 'created_at']
    search_fields = ['user__username', 'course__title', 'comment']
    readonly_fields = ['created_at', 'updated_at']

    def comment_preview(self, obj):
        return obj.comment[:50] + '...' if len(obj.comment) > 50 else obj.comment

    comment_preview.short_description = _('التعليق')