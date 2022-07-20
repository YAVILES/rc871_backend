import factory

from apps.security.models import User


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = 'admin'
    name = 'Admin'
    last_name = 'User'
    email = "yonathanaviles123@gmail.com"
