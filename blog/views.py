from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.db.models import Q, Count
from django.core.paginator import Paginator
from .models import Post, BlogCategory, PostComment
from .forms import PostCommentForm


def blog_list_view(request):
    """
    List all published blog posts
    Template: blog/post_list.html
    """
    posts = Post.objects.filter(status='published').select_related(
        'author', 'category'
    ).order_by('-published_at')

    # Category filter
    category_slug = request.GET.get('category')
    if category_slug:
        posts = posts.filter(category__slug=category_slug)

    # Search
    search_query = request.GET.get('q')
    if search_query:
        posts = posts.filter(
            Q(title__icontains=search_query) |
            Q(title_en__icontains=search_query) |
            Q(excerpt__icontains=search_query) |
            Q(content__icontains=search_query)
        )

    # Pagination
    paginator = Paginator(posts, 9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Get categories
    categories = BlogCategory.objects.annotate(
        post_count=Count('posts')
    ).filter(post_count__gt=0)

    # Featured posts
    featured_posts = Post.objects.filter(
        status='published',
        is_featured=True
    ).order_by('-published_at')[:3]

    context = {
        'page_obj': page_obj,
        'categories': categories,
        'featured_posts': featured_posts,
        'selected_category': category_slug,
        'search_query': search_query,
    }
    return render(request, 'blog/post_list.html', context)


def blog_detail_view(request, slug):
    """
    Detailed blog post view
    Template: blog/post_detail.html
    """
    post = get_object_or_404(
        Post.objects.select_related('author', 'category'),
        slug=slug,
        status='published'
    )

    # Increment views count
    post.views_count += 1
    post.save(update_fields=['views_count'])

    # Get comments
    comments = post.comments.filter(
        is_approved=True,
        parent=None
    ).select_related('user').prefetch_related('replies')

    # Handle comment form
    if request.method == 'POST' and request.user.is_authenticated:
        form = PostCommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.user = request.user

            # Handle reply
            parent_id = request.POST.get('parent_id')
            if parent_id:
                comment.parent_id = parent_id

            comment.save()
            messages.success(request, _('تم إضافة التعليق بنجاح'))
            return redirect('blog:detail', slug=slug)
    else:
        form = PostCommentForm()

    # Related posts
    related_posts = Post.objects.filter(
        status='published',
        category=post.category
    ).exclude(id=post.id).order_by('-published_at')[:3]

    context = {
        'post': post,
        'comments': comments,
        'form': form,
        'related_posts': related_posts,
    }
    return render(request, 'blog/post_detail.html', context)


def blog_category_view(request, slug):
    """
    View posts by category
    Template: blog/category.html
    """
    category = get_object_or_404(BlogCategory, slug=slug)
    posts = Post.objects.filter(
        category=category,
        status='published'
    ).select_related('author').order_by('-published_at')

    # Pagination
    paginator = Paginator(posts, 9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'category': category,
        'page_obj': page_obj,
    }
    return render(request, 'blog/category.html', context)