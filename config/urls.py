"""
Main URL configuration for Academy project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns
from django.views.i18n import set_language

urlpatterns = [
    path('admin/', admin.site.urls),
    path('i18n/setlang/', set_language, name='set_language'),
    path('tinymce/', include('tinymce.urls')),
]

# URL patterns with internationalization support
urlpatterns += i18n_patterns(
    path('', include('courses.urls')),
    path('accounts/', include('allauth.urls')),
    path('blog/', include('blog.urls')),
    path('payments/', include('payments.urls')),
    path('users/', include('users.urls')),
    prefix_default_language=True
)

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Admin site customization
admin.site.site_header = "لوحة تحكم الأكاديمية"
admin.site.site_title = "إدارة الأكاديمية"
admin.site.index_title = "مرحباً بك في لوحة التحكم"