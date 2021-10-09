# coding=utf-8
from constance.admin import config
from constance.backends.database.models import Constance
from django.contrib.auth import password_validation
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.db import transaction
from django.db.models import Q, Value
from django.db.models.functions import Concat
from django.utils.translation import ugettext_lazy as _
from django_restql.mixins import DynamicFieldsMixin
from drf_extra_fields import geo_fields
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from apis.client.serializers import ClientDefaultSerializer, ClientSettingSerializer, ClientSellerSerializer
from apps.checkout.models import Order
from apps.client.models import Client
from apps.core.models import Module, WorkFlow, Menu
from apps.security.models import User, RecoveryQuestions, UserRecoveryQuestions
from apps.notification.tasks import send_email


class RoleDefaultSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = serializers.ALL_FIELDS


class RoleUserSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ('id', 'name',)


class RoleFullSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    name = serializers.CharField(max_length=255, required=False)

    class Meta:
        model = Group
        fields = serializers.ALL_FIELDS


class UserCreateSerializer(serializers.ModelSerializer):
    groups = serializers.PrimaryKeyRelatedField(
        queryset=Group.objects.all(), many=True, required=False, write_only=True
    )
    code = serializers.CharField(max_length=255, required=False)
    password = serializers.CharField(max_length=255, write_only=True, required=False)
    point = geo_fields.PointField(required=False)
    is_superuser = serializers.BooleanField(required=False, read_only=True)
    info = ClientSettingSerializer(write_only=True, required=False)
    email = serializers.EmailField()
    email_alternative = serializers.EmailField(required=False)

    def validate(self, attrs):
        password = attrs.get('password')
        if password:
            try:
                password_validation.validate_password(password)
            except ValidationError as error:
                raise serializers.ValidationError(detail={"error": error.messages})
        return attrs

    def create(self, validated_data):
        password = validated_data.get('password')
        email = validated_data.get('email')
        email_alternative = validated_data.get('email_alternative')
        validated_data['email'] = str(email).lower()
        validated_data['email_alternative'] = str(email_alternative).lower()
        try:
            with transaction.atomic():
                user = super(UserCreateSerializer, self).create(validated_data)
                if password:
                    user.set_password(password)
                    user.save(update_fields=['password'])
                    send_email.delay('Clave Temporal B2B', password, [email, email_alternative])
        except ValidationError as error:
            raise serializers.ValidationError(detail={"error": error.messages})
        return validated_data

    class Meta:
        model = User
        fields = ('id', 'code', 'email', 'email_alternative', 'password', 'name', 'last_name', 'full_name', 'direction',
                  'telephone', 'phone', 'point', 'is_superuser', 'groups', 'is_client', 'info',)


class UserDefaultSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    groups = RoleUserSerializer(many=True, read_only=True)
    password = serializers.CharField(max_length=255, write_only=True, required=False)
    point = geo_fields.PointField(required=False)
    is_superuser = serializers.BooleanField(required=False, read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = User
        fields = ('id', 'code', 'email', 'password', 'name', 'last_name', 'full_name', 'direction', 'telephone',
                  'phone', 'point', 'is_superuser', 'groups', 'status', 'status_display', 'is_client', 'info',
                  'created', 'updated',)


class UserSimpleSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    point = geo_fields.PointField(required=False)
    is_superuser = serializers.BooleanField(required=False, read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = User
        fields = ('id', 'code', 'email', 'name', 'last_name', 'full_name', 'direction', 'telephone', 'phone', 'point',
                  'is_superuser', 'status', 'status_display', 'is_client', 'info', 'created', 'updated',)


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        super().validate(attrs)
        refresh = self.get_token(self.user)

        return {
            'token': str(refresh.access_token),
            'refresh': str(refresh),
            'jwt_id': self.user.jwt_id,
            'info': None,
            'danger': None,
            'warn': [],
            'name': self.user.full_name,
            "is_superuser": self.user.is_superuser,
        }


class UserAssignQuestionsDefaultSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(required=False)
    answer = serializers.CharField(max_length=255, required=True)

    class Meta:
        model = UserRecoveryQuestions
        fields = ('id', 'question', 'answer',)


class UserQuestionsDefaultSerializer(serializers.ModelSerializer):
    questions = serializers.SerializerMethodField()

    def get_questions(self, obj: 'User'):
        return UserAssignQuestionsDefaultSerializer(
            UserRecoveryQuestions.objects.filter(user_id=obj.id),
            many=True
        ).data

    class Meta:
        model = User
        fields = ('questions',)


class ChangeRecoveryCodeSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True)

    def validate(self, attrs):
        super().validate(attrs)
        try:
            user = User.objects.get(
                Q(email=attrs.get('email')) | Q(email_alternative=attrs.get('email'))
            )
        except:
            raise serializers.ValidationError(detail={"email": _('email invalid')})

        return attrs

    class Meta:
        model = User
        fields = ('email',)


class ValidSecurityCodeSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True)
    code = serializers.CharField(max_length=8, required=True)

    def validate(self, attrs):
        super().validate(attrs)
        code = attrs.get('code')
        email = attrs.get('email')
        try:
            user = User.objects.get(Q(email=email) | Q(email_alternative=email))
        except:
            raise serializers.ValidationError(detail={"email": _('email invalid')})
        try:
            if code == user.security_code:
                user.is_verified_security_code = True
                user.save(update_fields=['is_verified_security_code'])
            else:
                raise serializers.ValidationError(detail={"code": _('code invalid')})
        except:
            raise serializers.ValidationError(detail={"code": _('code invalid')})

        return attrs

    class Meta:
        model = User
        fields = ('email', 'code',)


class ChangePasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(max_length=255, required=True)

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        email = validated_data.get('email')
        email = str(email).lower()
        password = validated_data.get('password')
        try:
            password_validation.validate_password(password)
        except ValidationError as error:
            raise serializers.ValidationError(detail={"error": error.messages})
        try:
            user = User.objects.get(Q(email=email) | Q(email_alternative=email))
        except Exception as e:
            raise serializers.ValidationError(detail={"error": _('email invalid')})

        if user.is_verified_security_code or user.is_verified_recovery_questions or not user.is_verified:
            if user.is_verified_security_code:
                user.is_verified_security_code = False
            else:
                user.is_verified_recovery_questions = False
            user.set_password(password)
            user.save(update_fields=['password', 'is_verified_security_code', 'is_verified_recovery_questions'])
        else:
            raise serializers.ValidationError(detail={"error": _('user invalid')})
        return {'password': '', 'email': email}

    class Meta:
        fields = ('email', 'password',)


class StartDayClientSerializer(serializers.Serializer):
    planned_clients = ClientSellerSerializer(read_only=True)
    unplanned_clients = ClientSellerSerializer(read_only=True)

    class Meta:
        fields = ('planned_clients', 'unplanned_clients',)
