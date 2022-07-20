from django.test import TestCase, Client
from tests.factories import UserFactory


class UserTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = UserFactory.create()

    def test_user_creation(self):
        self.assertEqual(self.user.email, "yonathanaviles123@gmail.com")
        self.assertEqual(self.user.is_staff, False)

    def test_login(self):
        self.user.set_password('admin123')
        self.user.save(update_fields=['password'])
        response = self.client.post(
            '/api/token/',
            {
                "username": "admin",
                "password": "admin123"
            }
        )
        self.assertEqual(response.status_code, 200)

    def test_user_list(self):
        self.user.set_password('admin123')
        self.user.save(update_fields=['password'])
        response = self.client.get(
            '/api/security/user/'
        )
        self.assertEqual(response.status_code, 200)
