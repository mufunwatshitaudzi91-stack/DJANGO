from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse


class ProfileTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('pat', 'pat@example.com', 'Library#2026x')

    def test_profile_requires_login(self):
        url = reverse('profile')
        response = self.client.get(url)
        self.assertRedirects(response, f"{reverse('login')}?next={url}")

    def test_profile_page_loads_for_logged_in_user(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('profile'))
        self.assertContains(response, 'pat')

    def test_update_profile(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse('profile'), {
            'first_name': 'Pat', 'last_name': 'Jones', 'email': 'pat@example.com',
            'bio': 'I love reading.', 'location': 'Pretoria', 'birth_date': '',
        })
        self.assertRedirects(response, reverse('profile'))
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, 'Pat')
        self.assertEqual(self.user.profile.bio, 'I love reading.')

    def test_cannot_use_someone_elses_email(self):
        User.objects.create_user('other', 'other@example.com', 'Library#2026x')
        self.client.force_login(self.user)
        response = self.client.post(reverse('profile'), {
            'first_name': '', 'last_name': '', 'email': 'other@example.com',
            'bio': '', 'location': '', 'birth_date': '',
        })
        self.assertContains(response, 'This email is already registered.')