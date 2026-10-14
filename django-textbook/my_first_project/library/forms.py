from datetime import date

from django import forms
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