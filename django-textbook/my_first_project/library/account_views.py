from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect, render

from .account_forms import ProfileUpdateForm, UserUpdateForm
from .models import UserProfile


class RememberMeLoginView(LoginView):
    """Login page with a 'Remember me' checkbox."""

    def form_valid(self, form):
        response = super().form_valid(form)  # logs the user in
        if self.request.POST.get('remember_me'):
            self.request.session.set_expiry(60 * 60 * 24 * 30)  # 30 days
        else:
            self.request.session.set_expiry(0)  # until the browser closes
        return response


@login_required
def profile(request):
    """Show and edit the logged-in user's own profile."""
    # get_or_create covers older accounts that were made before profiles were automatic
    profile_obj, _ = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileUpdateForm(request.POST, instance=profile_obj)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your profile was updated.')
            return redirect('profile')
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileUpdateForm(instance=profile_obj)

    return render(request, 'registration/profile.html', {
        'user_form': user_form,
        'profile_form': profile_form,
    })