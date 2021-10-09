from threading import local

from django.utils.deprecation import MiddlewareMixin
from django.utils.functional import SimpleLazyObject
from django.contrib.auth import get_user

from django.core.handlers.wsgi import WSGIRequest
from rest_framework.authentication import TokenAuthentication
from rest_framework_simplejwt.authentication import JWTAuthentication


my_local_global = local()


class JWTAuthenticationMiddleware(MiddlewareMixin):

    def process_request(self, request):
        request.user = SimpleLazyObject(
            lambda: self.__class__.get_jwt_user(request))

    @staticmethod
    def get_jwt_user(request):
        user = get_user(request)
        if user.is_authenticated:
            return user
        jwt_authentication = JWTAuthentication()
        if jwt_authentication.get_header(request):
            user, jwt = jwt_authentication.authenticate(request)
        return user


class RestAuthMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    @staticmethod
    def get_user(request):
        user = get_user(request)
        if user.is_authenticated:
            return user

        token_authentication = TokenAuthentication()
        try:
            user, token = token_authentication.authenticate(request)
        except:
            pass
        return user

    def __call__(self, request):
        request.user = SimpleLazyObject(lambda: self.__class__.get_user(request))

        response = self.get_response(request)
        return response