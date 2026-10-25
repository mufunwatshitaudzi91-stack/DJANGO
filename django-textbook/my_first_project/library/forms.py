from datetime import date

from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password

from .models import Book


class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = [
            'title', 'subtitle', 'isbn', 'author', 'co_authors', 'publisher',
            'publication_date', 'genre', 'pages', 'language', 'summary',
            'rating', 'is_available', 'cover_image',
        ]
        widgets = {
            'publication_date': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'summary': forms.Textarea(attrs={'rows': 4}),
        }

    def clean_title(self):
        return self.cleaned_data['title'].strip()

    def clean_isbn(self):
        isbn = self.cleaned_data['isbn'].strip()
        if not isbn.isdigit() or len(isbn) != 13:
            raise forms.ValidationError('ISBN must be exactly 13 digits (numbers only).')
        return isbn

    def clean_publication_date(self):
        pub_date = self.cleaned_data['publication_date']
        if pub_date > date.today():
            raise forms.ValidationError('Publication date cannot be in the future.')
        return pub_date


class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput, label='Password',
        validators=[validate_password],
    )
    password_confirm = forms.CharField(
        widget=forms.PasswordInput, label='Confirm password',
    )
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('This email is already registered.')
        return email

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')
        if password and password_confirm and password != password_confirm:
            self.add_error('password_confirm', 'Passwords do not match.')
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])  # stores a hash, never the plain password
        if commit:
            user.save()
        return user