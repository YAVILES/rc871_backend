from constance.backends.database.models import Constance
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import transaction
from django_restql.mixins import DynamicFieldsMixin
from money.currency import CurrencyHelper, Currency
from rest_framework import serializers, fields
from apps.core.models import Policy, Vehicle, Plan
from apps.core.serializers import PolicyDefaultSerializer
from apps.payment.models import Bank, Payment, METHODS
from apps.security.models import User
from apps.security.serializers import UserSimpleSerializer


class BankDefaultSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    image = serializers.ImageField(required=False)
    image_display = serializers.SerializerMethodField(required=False, read_only=True)
    status_display = serializers.CharField(max_length=255, read_only=True, source="get_status_display")
    coins = fields.MultipleChoiceField(choices=Bank.COINS_VALUES)
    coins_display = serializers.CharField(max_length=255, source="get_coins_display", read_only=True)
    methods = fields.MultipleChoiceField(choices=METHODS)
    methods_display = serializers.CharField(max_length=255, source="get_methods_display", read_only=True)

    def get_image_display(self, obj: Bank):
        if obj.image and hasattr(obj.image, 'url'):
            image_url = obj.image.url
            return image_url
        else:
            return None

    class Meta:
        model = Bank
        fields = serializers.ALL_FIELDS


class PaymentDefaultSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault(), write_only=True)
    archive_display = serializers.SerializerMethodField(read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    coin_display = serializers.SerializerMethodField(read_only=True)
    method_display = serializers.CharField(source='get_method_display', read_only=True)
    user_display = UserSimpleSerializer(read_only=True, source="user")
    bank_display = BankDefaultSerializer(read_only=True, source="bank")
    policy_display = PolicyDefaultSerializer(read_only=True, source="policy")
    amount_display = serializers.CharField(read_only=True)
    change_factor_display = serializers.CharField(read_only=True)
    amount_full_display = serializers.CharField(read_only=True)
    total_full_bs_display = serializers.CharField(read_only=True)

    def get_coin_display(self, obj: Payment):
        return {
            'value': obj.coin,
            'description': CurrencyHelper._CURRENCY_DATA[Currency[obj.coin]]['display_name']
        }

    def get_archive_display(self, obj: Payment):
        request = self.context.get('request')
        if obj.archive and hasattr(obj.archive, 'url'):
            archive_url = obj.archive.url
            return request.build_absolute_uri(archive_url)
        else:
            return None

    class Meta:
        model = Payment
        fields = serializers.ALL_FIELDS


class PaymentSimpleSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault(), write_only=True)
    archive_display = serializers.SerializerMethodField(read_only=True)
    archive = serializers.SerializerMethodField(read_only=True)
    coin_display = serializers.CharField(source='get_coin_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    user_display = UserSimpleSerializer(read_only=True)
    bank_display = BankDefaultSerializer(read_only=True)
    method_display = serializers.CharField(source='get_method_display', read_only=True)

    def get_archive_display(self, obj: 'Payment'):
        request = self.context.get('request')
        if obj.archive and hasattr(obj.archive, 'url'):
            archive_url = obj.archive.url
            return request.build_absolute_uri(archive_url)
        else:
            return None

    class Meta:
        model = Payment
        fields = serializers.ALL_FIELDS


class PaymentEditSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    number = serializers.IntegerField(read_only=True)
    archive = serializers.FileField(required=False)
    reference = serializers.CharField(max_length=255, required=False)
    coin = serializers.CharField(required=False, default=settings.CURRENCY.value)
    bank = serializers.PrimaryKeyRelatedField(
        queryset=Bank.objects.all(),
        allow_null=True,
        write_only=True,
        required=False
    )
    policy = serializers.PrimaryKeyRelatedField(
        queryset=Policy.objects.all(),
        allow_null=True,
        write_only=True,
        required=False
    )
    plan = serializers.PrimaryKeyRelatedField(
        queryset=Plan.objects.all(),
        allow_null=True,
        write_only=True,
        required=False
    )
    vehicle = serializers.PrimaryKeyRelatedField(
        queryset=Vehicle.objects.all(),
        allow_null=True,
        write_only=True,
        required=False
    )
    user = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        required=False,
        allow_null=True,
        default=None
    )

    def create(self, validated_data):
        try:
            with transaction.atomic():
                plan = validated_data.pop('plan')
                vehicle = validated_data.pop('vehicle')
                policy = validated_data.get('policy')
                if not policy:
                    policy = PolicyDefaultSerializer(context=self.context).create({"plan": plan, "vehicle": vehicle})
                    validated_data["policy"] = policy
                validated_data["amount"] = policy.total_amount
                change_factor = Constance.objects.get(key="CHANGE_FACTOR").value
                validated_data['change_factor'] = change_factor
                payment = super(PaymentEditSerializer, self).create(validated_data)
        except ValidationError as error:
            raise serializers.ValidationError(detail={"error": error.messages})
        return payment

    class Meta:
        model = Payment
        exclude = ('created', 'updated', 'amount',)
