from django.urls import path
from . import views

app_name = 'blog'

urlpatterns = [
    path('', views.blog_list_view, name='list'),
    path('post/<slug:slug>/', views.blog_detail_view, name='detail'),
    path('category/<slug:slug>/', views.blog_category_view, name='category'),
]
