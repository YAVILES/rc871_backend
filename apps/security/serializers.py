# coding=utf-8
from django.contrib.auth import password_validation
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from django_restql.mixins import DynamicFieldsMixin
from drf_extra_fields import geo_fields
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from apps.core.models import Municipality, BranchOffice
from apps.security.models import User, Workflow, Role, Module


class MunicipalityUserSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    number = serializers.IntegerField(read_only=True)

    class Meta:
        model = Municipality
        fields = serializers.ALL_FIELDS


class ModuleDefaultSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    class Meta:
        model = Module
        fields = serializers.ALL_FIELDS


class WorkflowDefaultSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    module = serializers.PrimaryKeyRelatedField(
        queryset=Module.objects.all(), required=False
    )
    module_display = ModuleDefaultSerializer(read_only=True, source="module")

    class Meta:
        model = Workflow
        fields = serializers.ALL_FIELDS


class RoleDefaultSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    workflows = serializers.PrimaryKeyRelatedField(
        queryset=Workflow.objects.all(), many=True, required=False
    )
    workflows_display = WorkflowDefaultSerializer(many=True, read_only=True, source="workflows")

    class Meta:
        model = Role
        fields = serializers.ALL_FIELDS


class RoleUserSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    workflows_display = WorkflowDefaultSerializer(many=True, read_only=True, source="workflows")

    class Meta:
        model = Role
        fields = ('id', 'name', 'workflows', 'workflows_display',)


class RoleFullSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    name = serializers.CharField(max_length=255, required=False)
    workflows_display = WorkflowDefaultSerializer(many=True, read_only=True, source="workflows")

    class Meta:
        model = Role
        fields = serializers.ALL_FIELDS


class UserCreateClientSerializer(serializers.ModelSerializer):
    roles = serializers.PrimaryKeyRelatedField(
        queryset=Role.objects.all(), many=True, required=False, write_only=True
    )
    document_type = serializers.CharField(max_length=1, default=User.VENEZUELAN)
    username = serializers.CharField(max_length=255, required=False)
    identification_number = serializers.CharField(max_length=255, required=False, allow_null=True, allow_blank=True)
    password = serializers.CharField(max_length=255, write_only=True, required=False)
    point = geo_fields.PointField(required=False)
    is_superuser = serializers.BooleanField(required=False)
    email = serializers.EmailField()
    email_alternative = serializers.EmailField(required=False)
    photo = serializers.ImageField(required=False)

    def validate(self, attrs):
        password = attrs.get('password')
        if password:
            try:
                password_validation.validate_password(password)
            except ValidationError as error:
                raise serializers.ValidationError(detail={"error": error.messages})
        return attrs

    def create(self, validated_data):
        if User.objects.filter(username=validated_data.get('username')).exists():
            raise serializers.ValidationError(
                detail={"error": 'El usuario ' + validated_data.get('username') + ' ya existe'}
            )

        password = validated_data.get('password', None)
        if password is None:
            validated_data['password'] = validated_data.get('identification_card')
        email = validated_data.get('email')
        username = validated_data.pop('username', None)
        email_alternative = validated_data.pop('email_alternative', None)
        if username:
            validated_data['username'] = str(username).lower()
        validated_data['email'] = str(email).lower()
        if email_alternative:
            validated_data['email_alternative'] = str(email_alternative).lower()
        validated_data['is_staff'] = False
        try:
            with transaction.atomic():
                user = super(UserCreateClientSerializer, self).create(validated_data)
                if password:
                    user.set_password(password)
                    user.save(update_fields=['password'])
        except ValidationError as error:
            raise serializers.ValidationError(detail={"error": error.messages})
        return user

    class Meta:
        model = User
        fields = ('id', 'document_type', 'identification_number', 'username', 'email', 'email_alternative', 'photo', 'password', 'name',
                  'last_name', 'full_name', 'direction', 'telephone', 'phone', 'point', 'is_superuser', 'roles',
                  'info',)


class UserCreateSerializer(serializers.ModelSerializer):
    roles = serializers.PrimaryKeyRelatedField(
        queryset=Role.objects.all(), many=True, required=False, write_only=True
    )
    username = serializers.CharField(max_length=255, required=False)
    password = serializers.CharField(max_length=255, write_only=True, required=False)
    point = geo_fields.PointField(required=False)
    is_superuser = serializers.BooleanField(required=False)
    email = serializers.EmailField()
    email_alternative = serializers.EmailField(required=False)
    photo = serializers.ImageField(required=False)
    branch_office = serializers.PrimaryKeyRelatedField(
        queryset=BranchOffice.objects.all(), required=True
    )

    def validate(self, attrs):
        password = attrs.get('password')
        if password:
            try:
                password_validation.validate_password(password)
            except ValidationError as error:
                raise serializers.ValidationError(detail={"error": error.messages})
        return attrs

    def create(self, validated_data):
        if User.objects.filter(username=validated_data.get('username')).exists():
            raise serializers.ValidationError(
                detail={"error": 'El usuario ' + validated_data.get('username') + ' ya existe'}
            )

        password = validated_data.get('password')
        if password is None:
            validated_data['password'] = validated_data.get('identification_card')
        email = validated_data.get('email')
        username = validated_data.pop('username', None)
        if username:
            validated_data['username'] = str(username).lower()
        email_alternative = validated_data.pop('email_alternative', None)
        validated_data['email'] = str(email).lower()
        if email_alternative:
            validated_data['email_alternative'] = str(email_alternative).lower()
        validated_data['is_staff'] = True
        try:
            with transaction.atomic():
                user = super(UserCreateSerializer, self).create(validated_data)
                if password:
                    user.set_password(password)
                    user.save(update_fields=['password'])
        except ValidationError as error:
            raise serializers.ValidationError(detail={"error": error.messages})
        return user

    class Meta:
        model = User
        fields = ('id', 'username', 'document_type', 'identification_number', 'email', 'email_alternative', 'photo',
                  'password', 'name', 'last_name', 'full_name', 'direction', 'telephone', 'phone', 'branch_office',
                  'point', 'is_superuser', 'roles', 'info', 'is_adviser',)


class BranchOfficeUserSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    number = serializers.IntegerField(read_only=True)

    class Meta:
        model = BranchOffice
        fields = serializers.ALL_FIELDS


class UserDefaultSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    roles_display = RoleUserSerializer(many=True, read_only=True, source="roles")
    password = serializers.CharField(max_length=255, write_only=True, required=False)
    point = geo_fields.PointField(required=False)
    is_superuser = serializers.BooleanField(required=False, read_only=True)
    branch_office = serializers.PrimaryKeyRelatedField(
        queryset=BranchOffice.objects.all(), required=True
    )
    full_name = serializers.CharField(max_length=255, read_only=True)
    branch_office_display = BranchOfficeUserSerializer(read_only=True, source='branch_office')
    municipality = serializers.PrimaryKeyRelatedField(
        queryset=Municipality.objects.all(), required=True
    )
    municipality_display = MunicipalityUserSerializer(read_only=True, source='municipality')

    class Meta:
        model = User
        fields = serializers.ALL_FIELDS


class ClientDefaultSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    password = serializers.CharField(max_length=255, write_only=True, required=False)
    point = geo_fields.PointField(required=False)

    class Meta:
        model = User
        fields = ('id', 'username', 'document_type', 'identification_number', 'email', 'email_alternative', 'password', 'name',
                  'last_name', 'full_name', 'direction', 'telephone', 'phone', 'point', 'info', 'created', 'updated',
                  'is_active', 'photo',)


class UserSimpleSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    point = geo_fields.PointField(required=False)
    is_superuser = serializers.BooleanField(required=False, read_only=True)
    roles_display = RoleDefaultSerializer(many=True, read_only=True, source="roles")

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'name', 'last_name', 'full_name', 'document_type', 'identification_number', 'direction',
                  'telephone', 'phone', 'is_active', 'is_superuser', 'is_staff', 'is_adviser',
                  'branch_office', 'info', 'roles', 'roles_display', 'created', 'updated', 'point',)


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
            'user': UserSimpleSerializer(self.user).data
        }


class ChangePasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(max_length=255, required=True)

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        email = validated_data.get('email')
        email = str(email).lower()
        password = validated_data.get('password')
        if password is None:
            validated_data['password'] = validated_data.get('identification_card')
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
