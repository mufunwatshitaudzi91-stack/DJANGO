from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Q
from django.shortcuts import redirect, render
from django.urls import reverse, reverse_lazy
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView,
)

from .forms import BookForm, UserRegistrationForm
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

        # Books this visitor opened recently, remembered in their session
        recent_ids = self.request.session.get('recent_books', [])
        books_by_id = Book.objects.in_bulk(recent_ids)
        context['recent_books'] = [books_by_id[i] for i in recent_ids if i in books_by_id]
        return context


class BookDetailView(DetailView):
    model = Book
    template_name = 'library/book_detail.html'
    context_object_name = 'book'

    def get_queryset(self):
        return super().get_queryset().select_related('author', 'publisher')

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        # Remember the last 5 books this visitor looked at, newest first
        recent = request.session.get('recent_books', [])
        if self.object.pk in recent:
            recent.remove(self.object.pk)
        recent.insert(0, self.object.pk)
        request.session['recent_books'] = recent[:5]
        return response


class RedirectToDetailMixin:
    """After saving, go to the book's detail page."""
    def get_success_url(self):
        return reverse('library:book-detail', args=[self.object.pk])


class BookCreateView(PermissionRequiredMixin, SuccessMessageMixin,
                     RedirectToDetailMixin, CreateView):
    model = Book
    form_class = BookForm
    template_name = 'library/book_form.html'
    permission_required = 'library.add_book'
    success_message = 'Book "%(title)s" created!'
    extra_context = {'heading': 'Add a Book'}


class BookUpdateView(PermissionRequiredMixin, SuccessMessageMixin,
                     RedirectToDetailMixin, UpdateView):
    model = Book
    form_class = BookForm
    template_name = 'library/book_form.html'
    permission_required = 'library.change_book'
    success_message = 'Book "%(title)s" updated!'
    extra_context = {'heading': 'Edit Book'}


class BookDeleteView(PermissionRequiredMixin, DeleteView):
    model = Book
    template_name = 'library/book_confirm_delete.html'
    permission_required = 'library.delete_book'
    success_url = reverse_lazy('library:book-list')

    def form_valid(self, form):
        messages.success(self.request, f'Book "{self.object.title}" deleted.')
        return super().form_valid(form)


def register(request):
    """Sign-up page: create an account, then log the new user in."""
    if request.user.is_authenticated:
        return redirect('library:book-list')

    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Welcome, {user.username}! Your account was created.')
            return redirect('library:book-list')
    else:
        form = UserRegistrationForm()
    return render(request, 'registration/register.html', {'form': form})