from django.test import TestCase, Client

from apps.security.models import User
from tests.factories import UserAdminFactory


class UserTestCase(TestCase):
    def setUp(self):
        self.c = Client()
        self.user = UserAdminFactory.create()

    def test_user_creation(self):
        self.assertEqual(self.user.is_superuser, True)
        self.assertEqual(self.user.is_staff, True)

    def test_login(self):
        self.user.set_password('admin123')
        self.user.save(update_fields=['password'])
        response = self.c.post(
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

    def register_client(self):
        response = self.c.post(
            '/api/security/user/create_client/',
            {"name": "YONATHAN", "last_name": "AVILES", "identification_number": 23410567,
             "email": "example@example.com", "phone": "041444449876",
             "telephone": "02122346328", "municipality": "9b8643ac-04e8-4cfc-8b6d-209217509dfb",
             "direction": "Valencia", "username": "yaviles", "password": "yaviles123",
             "document_type": User.FOREIGN},
        )
        return response

    def test_create_client(self):
        response = self.register_client()
        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertEqual(data['document_type'], User.FOREIGN)
        self.assertEqual(data['direction'], 'Valencia')
        client = User.objects.get(pk=data['id'])
        self.assertEqual(client.is_staff, False)
        self.assertEqual(client.is_adviser, False)

