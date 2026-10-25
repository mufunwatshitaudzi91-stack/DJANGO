from datetime import date

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import Author, Book


class SessionTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        author = Author.objects.create(first_name='George', last_name='Orwell')
        cls.books = [
            Book.objects.create(
                title=f'Book {n}', isbn=f'978000000000{n}', author=author,
                publication_date=date(1949, 6, 8), genre='F', pages=100,
                summary='Summary.',
            )
            for n in range(6)
        ]
        User.objects.create_user('pat', password='Library#2026x')

    def view(self, book):
        return self.client.get(reverse('library:book-detail', args=[book.pk]))

    def test_viewing_a_book_is_remembered(self):
        self.view(self.books[0])
        self.assertEqual(self.client.session['recent_books'], [self.books[0].pk])

    def test_newest_first_and_no_duplicates(self):
        self.view(self.books[0])
        self.view(self.books[1])
        self.view(self.books[0])
        self.assertEqual(
            self.client.session['recent_books'], [self.books[0].pk, self.books[1].pk])

    def test_only_the_last_five_are_kept(self):
        for book in self.books:
            self.view(book)
        recent = self.client.session['recent_books']
        self.assertEqual(len(recent), 5)
        self.assertNotIn(self.books[0].pk, recent)

    def test_recent_box_appears_on_list(self):
        self.view(self.books[2])
        response = self.client.get(reverse('library:book-list'))
        self.assertContains(response, 'Recently viewed')

    def test_new_visitor_sees_no_recent_box(self):
        response = self.client.get(reverse('library:book-list'))
        self.assertNotContains(response, 'Recently viewed')

    def test_login_without_remember_me_ends_with_the_browser(self):
        self.client.post(reverse('login'),
                         {'username': 'pat', 'password': 'Library#2026x'})
        self.assertTrue(self.client.session.get_expire_at_browser_close())

    def test_login_with_remember_me_lasts_30_days(self):
        self.client.post(reverse('login'), {
            'username': 'pat', 'password': 'Library#2026x', 'remember_me': 'on'})
        self.assertEqual(self.client.session.get_expiry_age(), 60 * 60 * 24 * 30)