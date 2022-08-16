import factory

from apps.security.models import User


class UserAdminFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = 'admin'
    name = 'Admin'
    last_name = 'User'
    email = "admin@admin.com"
    is_staff = True
    is_superuser = True
