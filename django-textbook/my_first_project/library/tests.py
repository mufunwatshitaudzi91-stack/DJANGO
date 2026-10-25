from datetime import date

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .forms import BookForm
from .models import Author, Book
from .templatetags.library_extras import stars


class LibraryTestCase(TestCase):
    """Shared setup: one author and one book for every test."""

    @classmethod
    def setUpTestData(cls):
        cls.author = Author.objects.create(first_name='George', last_name='Orwell')
        cls.book = Book.objects.create(
            title='Nineteen Eighty-Four', isbn='9780451524935',
            author=cls.author, publication_date=date(1949, 6, 8),
            genre='SF', pages=328, summary='A dystopian novel.',
        )

    def valid_data(self, **overrides):
        data = {
            'title': 'Animal Farm', 'subtitle': '', 'isbn': '9780451526342',
            'author': self.author.pk, 'publication_date': '1945-08-17',
            'genre': 'F', 'pages': 112, 'language': 'English',
            'summary': 'A satirical novella.', 'rating': 3, 'is_available': 'on',
        }
        data.update(overrides)
        return data


class BookListViewTests(LibraryTestCase):
    def test_list_page_shows_books(self):
        response = self.client.get(reverse('library:book-list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Nineteen Eighty-Four')

    def test_search_finds_book_by_author(self):
        response = self.client.get(reverse('library:book-list'), {'q': 'orwell'})
        self.assertContains(response, 'Nineteen Eighty-Four')

    def test_search_with_no_match(self):
        response = self.client.get(reverse('library:book-list'), {'q': 'zzz'})
        self.assertNotContains(response, 'Nineteen Eighty-Four')
        self.assertContains(response, 'No books match your search.')

    def test_genre_filter(self):
        response = self.client.get(reverse('library:book-list'), {'genre': 'F'})
        self.assertNotContains(response, 'Nineteen Eighty-Four')


class BookDetailViewTests(LibraryTestCase):
    def test_detail_page(self):
        response = self.client.get(reverse('library:book-detail', args=[self.book.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Nineteen Eighty-Four')

    def test_missing_book_returns_404(self):
        response = self.client.get(reverse('library:book-detail', args=[9999]))
        self.assertEqual(response.status_code, 404)


class BookFormTests(LibraryTestCase):
    def test_valid_form(self):
        self.assertTrue(BookForm(data=self.valid_data()).is_valid())

    def test_isbn_must_be_13_digits(self):
        form = BookForm(data=self.valid_data(isbn='123'))
        self.assertFalse(form.is_valid())
        self.assertIn('isbn', form.errors)

    def test_future_date_rejected(self):
        form = BookForm(data=self.valid_data(publication_date='2999-01-01'))
        self.assertFalse(form.is_valid())
        self.assertIn('publication_date', form.errors)

    def test_duplicate_title_and_author_rejected(self):
        form = BookForm(data=self.valid_data(
            title='Nineteen Eighty-Four', isbn='9780000000001'))
        self.assertFalse(form.is_valid())


class BookEditViewTests(LibraryTestCase):
    """Adding and deleting now needs a logged-in user."""

    def setUp(self):
        user = User.objects.create_superuser('tester', 'tester@example.com', 'pass12345')
        self.client.force_login(user)

    def test_create_book(self):
        response = self.client.post(reverse('library:book-create'), self.valid_data())
        new_book = Book.objects.get(title='Animal Farm')
        self.assertRedirects(
            response, reverse('library:book-detail', args=[new_book.pk]))

    def test_delete_book(self):
        response = self.client.post(reverse('library:book-delete', args=[self.book.pk]))
        self.assertRedirects(response, reverse('library:book-list'))
        self.assertFalse(Book.objects.filter(pk=self.book.pk).exists())


class LoginRequiredTests(LibraryTestCase):
    """Logged-out visitors can read, but cannot add, edit or delete."""

    def test_list_is_public(self):
        response = self.client.get(reverse('library:book-list'))
        self.assertEqual(response.status_code, 200)

    def test_create_redirects_to_login(self):
        url = reverse('library:book-create')
        response = self.client.get(url)
        self.assertRedirects(response, f"{reverse('login')}?next={url}")

    def test_edit_redirects_to_login(self):
        url = reverse('library:book-update', args=[self.book.pk])
        response = self.client.get(url)
        self.assertRedirects(response, f"{reverse('login')}?next={url}")

    def test_delete_redirects_to_login_and_keeps_book(self):
        url = reverse('library:book-delete', args=[self.book.pk])
        response = self.client.post(url)
        self.assertRedirects(response, f"{reverse('login')}?next={url}")
        self.assertTrue(Book.objects.filter(pk=self.book.pk).exists())

    def test_login_page_loads(self):
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)

    def test_user_can_log_in_and_out(self):
        User.objects.create_user('reader', password='pass12345')
        response = self.client.post(
            reverse('login'), {'username': 'reader', 'password': 'pass12345'})
        self.assertRedirects(response, reverse('library:book-list'))
        response = self.client.post(reverse('logout'))
        self.assertRedirects(response, reverse('library:book-list'))


class StarsFilterTests(TestCase):
    def test_stars(self):
        self.assertEqual(stars(4), '★★★★☆')
        self.assertEqual(stars(0), '☆☆☆☆☆')
        self.assertEqual(stars('bad'), '')