from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import UserProfile


class RegistrationTests(TestCase):
    def valid_data(self, **overrides):
        data = {
            'username': 'newreader',
            'email': 'newreader@example.com',
            'first_name': 'New',
            'last_name': 'Reader',
            'password': 'Library#2026x',
            'password_confirm': 'Library#2026x',
        }
        data.update(overrides)
        return data

    def test_register_page_loads(self):
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)

    def test_successful_registration_creates_user_and_logs_in(self):
        response = self.client.post(reverse('register'), self.valid_data())
        self.assertRedirects(response, reverse('library:book-list'))
        user = User.objects.get(username='newreader')
        self.assertTrue(user.check_password('Library#2026x'))
        self.assertEqual(int(self.client.session['_auth_user_id']), user.pk)

    def test_profile_is_created_automatically(self):
        self.client.post(reverse('register'), self.valid_data())
        user = User.objects.get(username='newreader')
        self.assertTrue(UserProfile.objects.filter(user=user).exists())

    def test_password_is_not_stored_in_plain_text(self):
        self.client.post(reverse('register'), self.valid_data())
        user = User.objects.get(username='newreader')
        self.assertNotEqual(user.password, 'Library#2026x')

    def test_weak_password_is_rejected(self):
        response = self.client.post(
            reverse('register'),
            self.valid_data(password='12345678', password_confirm='12345678'))
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username='newreader').exists())

    def test_mismatched_passwords_are_rejected(self):
        response = self.client.post(
            reverse('register'), self.valid_data(password_confirm='Different#999'))
        self.assertContains(response, 'Passwords do not match.')
        self.assertFalse(User.objects.filter(username='newreader').exists())

    def test_duplicate_email_is_rejected(self):
        User.objects.create_user('existing', 'newreader@example.com', 'Library#2026x')
        response = self.client.post(reverse('register'), self.valid_data())
        self.assertContains(response, 'This email is already registered.')

    def test_logged_in_user_is_redirected_away(self):
        user = User.objects.create_user('already', password='Library#2026x')
        self.client.force_login(user)
        response = self.client.get(reverse('register'))
        self.assertRedirects(response, reverse('library:book-list'))