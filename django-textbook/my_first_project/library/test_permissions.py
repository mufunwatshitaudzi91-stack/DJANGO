from datetime import date

from django.contrib.auth.models import Group, Permission, User
from django.test import TestCase
from django.urls import reverse

from .models import Author, Book


class PermissionTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        author = Author.objects.create(first_name='George', last_name='Orwell')
        cls.book = Book.objects.create(
            title='Nineteen Eighty-Four', isbn='9780451524935', author=author,
            publication_date=date(1949, 6, 8), genre='SF', pages=328,
            summary='A dystopian novel.',
        )
        cls.reader = User.objects.create_user('reader', password='Library#2026x')
        cls.librarian = User.objects.create_user('librarian', password='Library#2026x')
        group = Group.objects.create(name='Librarians')
        group.permissions.set(Permission.objects.filter(
            content_type__app_label='library', content_type__model='book'))
        cls.librarian.groups.add(group)

    def test_reader_gets_403_on_create(self):
        self.client.force_login(self.reader)
        response = self.client.get(reverse('library:book-create'))
        self.assertEqual(response.status_code, 403)

    def test_reader_gets_403_on_edit(self):
        self.client.force_login(self.reader)
        response = self.client.get(reverse('library:book-update', args=[self.book.pk]))
        self.assertEqual(response.status_code, 403)

    def test_reader_cannot_delete(self):
        self.client.force_login(self.reader)
        response = self.client.post(reverse('library:book-delete', args=[self.book.pk]))
        self.assertEqual(response.status_code, 403)
        self.assertTrue(Book.objects.filter(pk=self.book.pk).exists())

    def test_librarian_can_open_create_form(self):
        self.client.force_login(self.librarian)
        response = self.client.get(reverse('library:book-create'))
        self.assertEqual(response.status_code, 200)

    def test_librarian_can_delete(self):
        self.client.force_login(self.librarian)
        response = self.client.post(reverse('library:book-delete', args=[self.book.pk]))
        self.assertRedirects(response, reverse('library:book-list'))
        self.assertFalse(Book.objects.filter(pk=self.book.pk).exists())

    def test_reader_does_not_see_add_book_link(self):
        self.client.force_login(self.reader)
        response = self.client.get(reverse('library:book-list'))
        self.assertNotContains(response, 'Add Book')

    def test_librarian_sees_add_book_link(self):
        self.client.force_login(self.librarian)
        response = self.client.get(reverse('library:book-list'))
        self.assertContains(response, 'Add Book')

    def test_detail_buttons_hidden_from_reader(self):
        self.client.force_login(self.reader)
        response = self.client.get(reverse('library:book-detail', args=[self.book.pk]))
        self.assertNotContains(response, 'Edit this book')
        self.assertNotContains(response, 'Delete this book')

    def test_detail_buttons_shown_to_librarian(self):
        self.client.force_login(self.librarian)
        response = self.client.get(reverse('library:book-detail', args=[self.book.pk]))
        self.assertContains(response, 'Edit this book')
        self.assertContains(response, 'Delete this book')