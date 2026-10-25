from django import forms
from django.contrib.auth.models import User

from .models import UserProfile


class UserUpdateForm(forms.ModelForm):
    """Edit the built-in User fields."""
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']

    def clean_email(self):
        email = self.cleaned_data['email']
        taken = User.objects.filter(email__iexact=email).exclude(pk=self.instance.pk)
        if taken.exists():
            raise forms.ValidationError('This email is already registered.')
        return email


class ProfileUpdateForm(forms.ModelForm):
    """Edit the extra profile fields from Chapter 2."""
    class Meta:
        model = UserProfile
        fields = ['bio', 'location', 'birth_date']
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'bio': forms.Textarea(attrs={'rows': 4}),
        }