from django.urls import path
from . import views, htmx_views

app_name = 'courses'

urlpatterns = [
    path('', views.home_view, name='home'),
    path('courses/', views.course_list_view, name='list'),
    path('course/<slug:slug>/', views.course_detail_view, name='detail'),
    path('course/<slug:course_slug>/lesson/<int:lesson_id>/', views.lesson_view, name='lesson'),
    path('course/<slug:course_slug>/review/', views.add_review_view, name='add_review'),
    path('category/<slug:slug>/', views.category_view, name='category'),

# HTMX Endpoints
    path('htmx/courses/', htmx_views.course_list_htmx, name='list_htmx'),
    path('htmx/search/', htmx_views.search_courses_htmx, name='search_htmx'),
    path('htmx/lesson/<int:lesson_id>/comment/', htmx_views.add_comment_htmx, name='add_comment_htmx'),
    path('htmx/lesson/<int:lesson_id>/comments/', htmx_views.load_more_comments, name='load_more_comments'),
    path('htmx/course/<slug:course_slug>/review/', htmx_views.add_review_htmx, name='add_review_htmx'),
    path('htmx/course/<slug:course_slug>/preview/', htmx_views.course_preview_htmx, name='preview_htmx'),
    path('htmx/lesson/<int:lesson_id>/progress/', htmx_views.update_progress_htmx, name='update_progress_htmx'),
    path('htmx/comment/<int:comment_id>/delete/', htmx_views.delete_comment_htmx, name='delete_comment_htmx'),
    path('htmx/course/<slug:course_slug>/lesson/<int:lesson_id>/content/', htmx_views.lesson_htmx_content, name='lesson_htmx_content'),
]

