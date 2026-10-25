from datetime import date

from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse

from .models import Author, Book


class SecurityTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.author = Author.objects.create(first_name='George', last_name='Orwell')
        cls.admin = User.objects.create_superuser(
            'boss', 'boss@example.com', 'Library#2026x')

    def make_book(self, title, isbn='9782222222222'):
        return Book.objects.create(
            title=title, isbn=isbn, author=self.author,
            publication_date=date(2000, 1, 1), genre='F', pages=100,
            summary='Summary.',
        )

    def test_html_in_a_title_is_escaped(self):
        """XSS: a <script> tag in a title must show as text, never run."""
        self.make_book('<script>alert("XSS")</script>')
        response = self.client.get(reverse('library:book-list'))
        self.assertNotContains(response, '<script>alert("XSS")</script>')
        self.assertContains(response, '&lt;script&gt;')

    def test_search_is_safe_from_sql_injection(self):
        self.make_book('Safe Book')
        response = self.client.get(
            reverse('library:book-list'), {'q': "' OR '1'='1"})
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'Safe Book')

        response = self.client.get(
            reverse('library:book-list'), {'q': "'; DROP TABLE library_book; --"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Book.objects.count(), 1)

    def test_post_without_csrf_token_is_rejected(self):
        csrf_client = Client(enforce_csrf_checks=True)
        csrf_client.force_login(self.admin)
        response = csrf_client.post(reverse('library:book-create'), {
            'title': 'No token', 'isbn': '9781111111111',
            'author': self.author.pk, 'publication_date': '1945-08-17',
            'genre': 'F', 'pages': 100, 'language': 'English',
            'summary': 'Summary.', 'rating': 3, 'is_available': 'on',
        })
        self.assertEqual(response.status_code, 403)
        self.assertFalse(Book.objects.filter(title='No token').exists())

    def test_session_cookie_is_httponly(self):
        self.client.post(reverse('login'),
                         {'username': 'boss', 'password': 'Library#2026x'})
        self.assertTrue(self.client.cookies['sessionid']['httponly'])

    def test_pages_cannot_be_framed(self):
        """Clickjacking: other sites may not show our pages inside a frame."""
        response = self.client.get(reverse('library:book-list'))
        self.assertEqual(response.headers['X-Frame-Options'], 'DENY')