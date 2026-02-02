from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from .forms import UserProfileForm


@login_required
def profile_view(request):
    """
    View for displaying and editing user profile
    Template: users/profile.html
    """
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, _('تم تحديث الملف الشخصي بنجاح'))
            return redirect('users:profile')
    else:
        form = UserProfileForm(instance=request.user)

    context = {
        'form': form,
        'user': request.user,
    }
    return render(request, 'users/profile.html', context)


@login_required
def dashboard_view(request):
    """
    User dashboard showing enrolled courses and progress
    Template: users/dashboard.html
    """
    enrolled_courses = request.user.enrolled_courses.all()

    context = {
        'enrolled_courses': enrolled_courses,
    }
    return render(request, 'users/dashboard.html', context)