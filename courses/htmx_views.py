"""
HTMX Views for dynamic course interactions
"""
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseForbidden
from django.template.loader import render_to_string
from django.views.decorators.http import require_http_methods
from .models import Course, Lesson, Comment, Review, Enrollment
from .forms import CommentForm, ReviewForm


def user_can_access_lesson(user, lesson):
    """Return True if user can access the lesson content/interactions."""
    if lesson.is_preview:
        return True

    if not user.is_authenticated:
        return False

    return Enrollment.objects.filter(
        user=user,
        course=lesson.course,
        is_active=True
    ).exists()


@require_http_methods(["GET"])
def course_list_htmx(request):
    """
    HTMX endpoint for dynamic course filtering
    """
    courses = Course.objects.filter(is_published=True).select_related('category', 'instructor')
    
    # Filters
    category_slug = request.GET.get('category')
    difficulty = request.GET.get('difficulty')
    search_query = request.GET.get('q')
    sort_by = request.GET.get('sort', '-created_at')
    
    if category_slug:
        courses = courses.filter(category__slug=category_slug)
    if difficulty:
        courses = courses.filter(difficulty=difficulty)
    if search_query:
        courses = courses.filter(title__icontains=search_query)
    
    courses = courses.order_by(sort_by)
    
    context = {'courses': courses}
    return render(request, 'courses/partials/course_grid.html', context)


@require_http_methods(["POST"])
@login_required
def add_comment_htmx(request, lesson_id):
    """
    HTMX endpoint for adding comments
    """
    lesson = get_object_or_404(Lesson, id=lesson_id)
    if not user_can_access_lesson(request.user, lesson):
        return HttpResponseForbidden('<div class="alert alert-danger">يجب شراء الدورة أولاً</div>')

    form = CommentForm(request.POST)

    if form.is_valid():
        comment = form.save(commit=False)
        comment.lesson = lesson
        comment.user = request.user
        
        parent_id = request.POST.get('parent_id')
        if parent_id:
            comment.parent_id = parent_id
        
        comment.save()
        
        # Return the new comment HTML
        context = {'comment': comment}
        html = render_to_string('courses/partials/comment_item.html', context, request=request)
        
        return HttpResponse(html, headers={'HX-Trigger': 'commentAdded'})
    
    return HttpResponse('<div class="alert alert-danger">حدث خطأ في إضافة التعليق</div>')


@require_http_methods(["GET"])
def load_more_comments(request, lesson_id):
    """
    HTMX endpoint for loading more comments
    """
    if not request.user.is_authenticated:
        return HttpResponseForbidden('<div class="alert alert-danger">يجب تسجيل الدخول أولاً</div>')

    lesson = get_object_or_404(Lesson, id=lesson_id)

    if not user_can_access_lesson(request.user, lesson):
        return HttpResponseForbidden('<div class="alert alert-danger">يجب شراء الدورة أولاً</div>')

    offset = int(request.GET.get('offset', 0))
    limit = 5
    
    comments = lesson.comments.filter(is_active=True, parent=None).select_related('user')[offset:offset+limit]
    
    context = {
        'comments': comments,
        'lesson': lesson,
        'offset': offset + limit
    }
    
    return render(request, 'courses/partials/comment_list.html', context)


@require_http_methods(["POST"])
@login_required
def add_review_htmx(request, course_slug):
    """
    HTMX endpoint for adding/updating review
    """
    course = get_object_or_404(Course, slug=course_slug, is_published=True)
    
    # Check if enrolled
    is_enrolled = Enrollment.objects.filter(
        user=request.user,
        course=course,
        is_active=True
    ).exists()
    
    if not is_enrolled:
        return HttpResponse('<div class="alert alert-danger">يجب التسجيل في الدورة أولاً</div>')
    
    review = Review.objects.filter(user=request.user, course=course).first()
    form = ReviewForm(request.POST, instance=review)
    
    if form.is_valid():
        review = form.save(commit=False)
        review.user = request.user
        review.course = course
        review.save()
        
        # Return updated reviews section
        reviews = course.reviews.select_related('user').all()
        avg_rating = course.average_rating
        
        context = {
            'reviews': reviews,
            'avg_rating': avg_rating,
            'course': course
        }
        
        html = render_to_string('courses/partials/reviews_section.html', context, request=request)
        return HttpResponse(html, headers={'HX-Trigger': 'reviewAdded'})
    
    return HttpResponse('<div class="alert alert-danger">حدث خطأ في إضافة التقييم</div>')


@require_http_methods(["GET"])
def search_courses_htmx(request):
    """
    HTMX endpoint for live search
    """
    query = request.GET.get('q', '')
    
    if len(query) < 2:
        return HttpResponse('')
    
    courses = Course.objects.filter(
        is_published=True,
        title__icontains=query
    ).select_related('category')[:5]
    
    context = {'courses': courses}
    return render(request, 'courses/partials/search_results.html', context)


@require_http_methods(["POST"])
@login_required
def toggle_wishlist_htmx(request, course_id):
    """
    HTMX endpoint for toggling wishlist
    """
    course = get_object_or_404(Course, id=course_id)
    
    # This would require a Wishlist model (simplified version)
    is_wishlisted = False  # Placeholder
    
    context = {
        'course': course,
        'is_wishlisted': not is_wishlisted
    }
    
    return render(request, 'courses/partials/wishlist_button.html', context)


@require_http_methods(["GET"])
def course_preview_htmx(request, course_slug):
    """
    HTMX endpoint for course preview modal
    """
    course = get_object_or_404(Course, slug=course_slug, is_published=True)
    preview_lessons = course.lessons.filter(is_preview=True)
    
    context = {
        'course': course,
        'preview_lessons': preview_lessons
    }
    
    return render(request, 'courses/partials/course_preview_modal.html', context)


@require_http_methods(["POST"])
@login_required
def update_progress_htmx(request, lesson_id):
    """
    HTMX endpoint for updating lesson progress
    """
    lesson = get_object_or_404(Lesson, id=lesson_id)
    
    enrollment = Enrollment.objects.filter(
        user=request.user,
        course=lesson.course,
        is_active=True
    ).first()
    
    if enrollment:
        # Update progress logic here
        completed = request.POST.get('completed') == 'true'
        
        # Simple progress calculation
        total_lessons = lesson.course.lessons.count()
        if total_lessons > 0:
            enrollment.progress = min(100, (enrollment.progress or 0) + (100 // total_lessons))
            enrollment.save()
        
        context = {
            'enrollment': enrollment,
            'course': lesson.course
        }
        
        return render(request, 'courses/partials/progress_bar.html', context)
    
    return HttpResponse('')


@require_http_methods(["DELETE"])
@login_required
def delete_comment_htmx(request, comment_id):
    """
    HTMX endpoint for deleting comment
    """
    comment = get_object_or_404(Comment, id=comment_id)
    
    if comment.user == request.user or request.user.is_staff:
        comment.is_active = False
        comment.save()
        return HttpResponse('', headers={'HX-Trigger': 'commentDeleted'})
    
    return HttpResponse('<div class="alert alert-danger">غير مصرح لك بحذف هذا التعليق</div>', status=403)


@require_http_methods(["GET"])
def lesson_htmx_content(request, course_slug, lesson_id):
    """
    HTMX endpoint for loading lesson content dynamically
    """
    if not request.user.is_authenticated:
        return HttpResponseForbidden('<div class="alert alert-danger">يجب تسجيل الدخول أولاً</div>')

    course = get_object_or_404(Course, slug=course_slug, is_published=True)
    lesson = get_object_or_404(Lesson, id=lesson_id, course=course)

    # Check access permissions
    is_enrolled = user_can_access_lesson(request.user, lesson)

    if not is_enrolled:
        return HttpResponseForbidden('<div class="alert alert-danger">يجب التسجيل في الدورة للوصول لهذا الدرس</div>')

    # Get all lessons for sidebar
    all_lessons = course.lessons.order_by('order', 'created_at')
    
    # Get comments
    comments = lesson.comments.filter(is_active=True, parent=None).select_related('user')[:5]
    
    context = {
        'course': course,
        'lesson': lesson,
        'all_lessons': all_lessons,
        'comments': comments,
        'is_enrolled': is_enrolled,
    }
    
    return render(request, 'courses/partials/lesson_content.html', context)
