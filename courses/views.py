from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.db.models import Q, Count, Avg
from .models import Course, Category, Lesson, Comment, Review, Enrollment
from .forms import CommentForm, ReviewForm


def home_view(request):
    """
    Homepage with featured courses
    Template: courses/home.html
    """
    featured_courses = Course.objects.filter(
        is_published=True,
        is_featured=True
    ).select_related('category', 'instructor')[:6]

    recent_courses = Course.objects.filter(
        is_published=True
    ).select_related('category', 'instructor').order_by('-created_at')[:8]

    categories = Category.objects.annotate(
        course_count=Count('courses')
    ).filter(course_count__gt=0)

    context = {
        'featured_courses': featured_courses,
        'recent_courses': recent_courses,
        'categories': categories,
    }
    return render(request, 'courses/home.html', context)


def course_list_view(request):
    """
    List all published courses with filtering
    Template: courses/course_list.html
    """
    courses = Course.objects.filter(is_published=True).select_related(
        'category', 'instructor'
    )

    # Category filter
    category_slug = request.GET.get('category')
    if category_slug:
        courses = courses.filter(category__slug=category_slug)

    # Difficulty filter
    difficulty = request.GET.get('difficulty')
    if difficulty:
        courses = courses.filter(difficulty=difficulty)

    # Search
    search_query = request.GET.get('q')
    if search_query:
        courses = courses.filter(
            Q(title__icontains=search_query) |
            Q(title_en__icontains=search_query) |
            Q(description__icontains=search_query)
        )

    # Sorting
    sort_by = request.GET.get('sort', '-created_at')
    if sort_by in ['-created_at', 'price', '-price', 'title']:
        courses = courses.order_by(sort_by)

    categories = Category.objects.all()

    context = {
        'courses': courses,
        'categories': categories,
        'selected_category': category_slug,
        'selected_difficulty': difficulty,
        'search_query': search_query,
    }
    return render(request, 'courses/course_list.html', context)


def course_detail_view(request, slug):
    """
    Detailed course view with lessons and reviews
    Template: courses/course_detail.html
    """
    course = get_object_or_404(
        Course.objects.select_related('category', 'instructor'),
        slug=slug,
        is_published=True
    )

    # Lessons are available if the course is published
    lessons = course.lessons.all().order_by('order', 'created_at')
    preview_lessons = lessons.filter(is_preview=True)

    # Check if user is enrolled
    is_enrolled = False
    if request.user.is_authenticated:
        is_enrolled = Enrollment.objects.filter(
            user=request.user,
            course=course,
            is_active=True
        ).exists()

    # Get reviews
    reviews = course.reviews.select_related('user').all()
    avg_rating = course.average_rating

    # Check if user has reviewed
    user_review = None
    if request.user.is_authenticated:
        user_review = reviews.filter(user=request.user).first()

    context = {
        'course': course,
        'lessons': lessons,
        'preview_lessons': preview_lessons,
        'is_enrolled': is_enrolled,
        'reviews': reviews,
        'avg_rating': avg_rating,
        'user_review': user_review,
    }
    return render(request, 'courses/course_detail.html', context)


@login_required
def lesson_view(request, course_slug, lesson_id):
    """
    View individual lesson (only for enrolled users)
    Template: courses/lesson.html
    """
    course = get_object_or_404(Course, slug=course_slug, is_published=True)
    lesson = get_object_or_404(Lesson, id=lesson_id, course=course)

    # Check enrollment or if it's a preview lesson
    is_enrolled = Enrollment.objects.filter(
        user=request.user,
        course=course,
        is_active=True
    ).exists()

    if not (is_enrolled or lesson.is_preview):
        messages.error(request, _('يجب التسجيل في الدورة لمشاهدة هذا الدرس'))
        return redirect('courses:detail', slug=course_slug)

    # Get comments
    comments = lesson.comments.filter(
        is_active=True,
        parent=None
    ).select_related('user').prefetch_related('replies')

    # Handle comment form
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.lesson = lesson
            comment.user = request.user

            # Handle reply
            parent_id = request.POST.get('parent_id')
            if parent_id:
                comment.parent_id = parent_id

            comment.save()
            messages.success(request, _('تم إضافة التعليق بنجاح'))
            return redirect('courses:lesson', course_slug=course_slug, lesson_id=lesson_id)
    else:
        form = CommentForm()

    # Get all lessons for navigation
    all_lessons = course.lessons.all()

    context = {
        'course': course,
        'lesson': lesson,
        'comments': comments,
        'form': form,
        'all_lessons': all_lessons,
    }
    return render(request, 'courses/lesson.html', context)


@login_required
def add_review_view(request, course_slug):
    """
    Add or update course review
    Template: courses/add_review.html
    """
    course = get_object_or_404(Course, slug=course_slug, is_published=True)

    # Check if enrolled
    is_enrolled = Enrollment.objects.filter(
        user=request.user,
        course=course,
        is_active=True
    ).exists()

    if not is_enrolled:
        messages.error(request, _('يجب التسجيل في الدورة لإضافة تقييم'))
        return redirect('courses:detail', slug=course_slug)

    # Get existing review
    review = Review.objects.filter(user=request.user, course=course).first()

    if request.method == 'POST':
        form = ReviewForm(request.POST, instance=review)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.course = course
            review.save()
            messages.success(request, _('تم إضافة التقييم بنجاح'))
            return redirect('courses:detail', slug=course_slug)
    else:
        form = ReviewForm(instance=review)

    context = {
        'course': course,
        'form': form,
        'review': review,
    }
    return render(request, 'courses/add_review.html', context)


def category_view(request, slug):
    """
    View courses by category
    Template: courses/category.html
    """
    category = get_object_or_404(Category, slug=slug)
    courses = Course.objects.filter(
        category=category,
        is_published=True
    ).select_related('instructor')

    context = {
        'category': category,
        'courses': courses,
    }
    return render(request, 'courses/category.html', context)