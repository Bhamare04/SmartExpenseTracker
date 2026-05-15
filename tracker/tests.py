from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


class RegistrationViewTests(TestCase):
    def test_register_logs_user_in_and_redirects_to_dashboard(self):
        response = self.client.post(
            reverse('register'),
            {
                'full_name': 'Test User',
                'username': 'testuser',
                'email': 'test@example.com',
                'mobile_number': '9999999999',
                'password1': 'StrongPass123',
                'password2': 'StrongPass123',
            },
        )

        self.assertRedirects(response, reverse('dashboard'))
        user = get_user_model().objects.get(username='testuser')
        self.assertEqual(int(self.client.session['_auth_user_id']), user.pk)
