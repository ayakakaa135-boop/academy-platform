from django.contrib import admin

# Register your models here.
from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import BlogCategory, Post, PostComment


@admin.register(BlogCategory)
class BlogCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'name_en', 'slug']
    search_fields = ['name', 'name_en']
    prepopulated_fields = {'slug': ('name_en',)}


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = [
        'title',
        'author',
        'category',
        'status',
        'is_featured',
        'views_count',
        'published_at',
        'created_at'
    ]
    list_filter = ['status', 'is_featured', 'category', 'created_at', 'published_at']
    search_fields = ['title', 'title_en', 'excerpt', 'content']
    prepopulated_fields = {'slug': ('title_en',)}
    readonly_fields = ['views_count', 'created_at', 'updated_at']
    date_hierarchy = 'published_at'

    fieldsets = (
        (_('معلومات أساسية'), {
            'fields': ('title', 'title_en', 'slug', 'author', 'category')
        }),
        (_('المحتوى'), {
            'fields': ('excerpt', 'excerpt_en', 'content', 'content_en', 'featured_image')
        }),
        (_('الحالة'), {
            'fields': ('status', 'is_featured', 'published_at')
        }),
        (_('SEO'), {
            'fields': ('meta_description', 'meta_keywords'),
            'classes': ('collapse',)
        }),
        (_('إحصائيات'), {
            'fields': ('views_count', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def save_model(self, request, obj, form, change):
        if not change:
            obj.author = request.user
        super().save_model(request, obj, form, change)


@admin.register(PostComment)
class PostCommentAdmin(admin.ModelAdmin):
    list_display = ['user', 'post', 'content_preview', 'is_approved', 'created_at']
    list_filter = ['is_approved', 'created_at']
    search_fields = ['user__username', 'post__title', 'content']
    readonly_fields = ['created_at', 'updated_at']

    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content

    content_preview.short_description = _('المحتوى')