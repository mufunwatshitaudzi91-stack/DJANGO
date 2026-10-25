from django.contrib.auth.models import User
from django.core import mail
from django.test import TestCase
from django.urls import reverse


class PasswordChangeTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('pat', 'pat@example.com', 'OldPass#2026x')

    def test_change_requires_login(self):
        url = reverse('password_change')
        response = self.client.get(url)
        self.assertRedirects(response, f"{reverse('login')}?next={url}")

    def test_change_password(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse('password_change'), {
            'old_password': 'OldPass#2026x',
            'new_password1': 'NewPass#2027y',
            'new_password2': 'NewPass#2027y',
        })
        self.assertRedirects(response, reverse('password_change_done'))
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('NewPass#2027y'))

    def test_wrong_old_password_is_rejected(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse('password_change'), {
            'old_password': 'wrong',
            'new_password1': 'NewPass#2027y',
            'new_password2': 'NewPass#2027y',
        })
        self.assertEqual(response.status_code, 200)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('OldPass#2026x'))


class PasswordResetTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('pat', 'pat@example.com', 'OldPass#2026x')

    def test_reset_sends_email_with_link(self):
        response = self.client.post(reverse('password_reset'), {'email': 'pat@example.com'})
        self.assertRedirects(response, reverse('password_reset_done'))
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('/accounts/reset/', mail.outbox[0].body)

    def test_unknown_email_looks_the_same_but_sends_nothing(self):
        response = self.client.post(reverse('password_reset'), {'email': 'nobody@example.com'})
        self.assertRedirects(response, reverse('password_reset_done'))
        self.assertEqual(len(mail.outbox), 0)