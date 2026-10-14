from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Q
from django.urls import reverse, reverse_lazy
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView,
)

from .forms import BookForm
from .models import Book


class BookListView(ListView):
    model = Book
    template_name = 'library/book_list.html'
    context_object_name = 'books'
    paginate_by = 12

    def get_queryset(self):
        queryset = super().get_queryset().select_related('author', 'publisher')
        search_query = self.request.GET.get('q', '')
        genre_filter = self.request.GET.get('genre', '')

        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) |
                Q(subtitle__icontains=search_query) |
                Q(author__first_name__icontains=search_query) |
                Q(author__last_name__icontains=search_query)
            )
        if genre_filter:
            queryset = queryset.filter(genre=genre_filter)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('q', '')
        context['genre_filter'] = self.request.GET.get('genre', '')
        context['genre_choices'] = Book.GENRE_CHOICES
        return context


class BookDetailView(DetailView):
    model = Book
    template_name = 'library/book_detail.html'
    context_object_name = 'book'

    def get_queryset(self):
        return super().get_queryset().select_related('author', 'publisher')


class RedirectToDetailMixin:
    """After saving, go to the book's detail page."""
    def get_success_url(self):
        return reverse('library:book-detail', args=[self.object.pk])


class BookCreateView(SuccessMessageMixin, RedirectToDetailMixin, CreateView):
    model = Book
    form_class = BookForm
    template_name = 'library/book_form.html'
    success_message = 'Book "%(title)s" created!'
    extra_context = {'heading': 'Add a Book'}


class BookUpdateView(SuccessMessageMixin, RedirectToDetailMixin, UpdateView):
    model = Book
    form_class = BookForm
    template_name = 'library/book_form.html'
    success_message = 'Book "%(title)s" updated!'
    extra_context = {'heading': 'Edit Book'}


class BookDeleteView(DeleteView):
    model = Book
    template_name = 'library/book_confirm_delete.html'
    success_url = reverse_lazy('library:book-list')

    def form_valid(self, form):
        messages.success(self.request, f'Book "{self.object.title}" deleted.')
        return super().form_valid(form)