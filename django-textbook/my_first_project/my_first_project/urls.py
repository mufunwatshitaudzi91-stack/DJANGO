"""
URL configuration for my_first_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path, include
from django.views.generic import RedirectView

from library import account_views
from library import views as library_views

urlpatterns = [
    path('', RedirectView.as_view(pattern_name='library:book-list'), name='home'),
    path('admin/', admin.site.urls),
    path('hello/', include('hello_world.urls')),
    path('library/', include('library.urls')),

    path('accounts/login/', account_views.RememberMeLoginView.as_view(), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('accounts/register/', library_views.register, name='register'),
    path('accounts/profile/', account_views.profile, name='profile'),

    path('accounts/password_change/',
         auth_views.PasswordChangeView.as_view(
             template_name='library/auth_form.html',
             extra_context={'title': 'Change your password',
                            'button': 'Change password'}),
         name='password_change'),
    path('accounts/password_change/done/',
         auth_views.PasswordChangeDoneView.as_view(
             template_name='library/auth_message.html',
             extra_context={'title': 'Password changed',
                            'message': 'Your password was changed successfully.',
                            'link_name': 'profile',
                            'link_text': 'Back to my profile'}),
         name='password_change_done'),

    path('accounts/password_reset/',
         auth_views.PasswordResetView.as_view(
             template_name='library/auth_form.html',
             email_template_name='library/password_reset_email.txt',
             subject_template_name='library/password_reset_subject.txt',
             extra_context={'title': 'Reset your password',
                            'intro': 'Enter your email address and we will send you a link to choose a new password.',
                            'button': 'Send reset link'}),
         name='password_reset'),
    path('accounts/password_reset/done/',
         auth_views.PasswordResetDoneView.as_view(
             template_name='library/auth_message.html',
             extra_context={'title': 'Check your email',
                            'message': 'If an account with that email address exists, we have sent a link to reset the password. During development the email is printed in the server terminal.',
                            'link_name': 'login',
                            'link_text': 'Back to log in'}),
         name='password_reset_done'),
    path('accounts/reset/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(
             template_name='library/auth_form.html',
             extra_context={'title': 'Choose a new password',
                            'button': 'Save new password'}),
         name='password_reset_confirm'),
    path('accounts/reset/done/',
         auth_views.PasswordResetCompleteView.as_view(
             template_name='library/auth_message.html',
             extra_context={'title': 'Password reset complete',
                            'message': 'Your new password is set. You can now log in.',
                            'link_name': 'login',
                            'link_text': 'Log in'}),
         name='password_reset_complete'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)