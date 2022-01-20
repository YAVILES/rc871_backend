# coding=utf-8
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django_restql.mixins import DynamicFieldsMixin
from rest_framework import serializers

from apps.core.models import Banner, BranchOffice, Use, Plan, Coverage, Premium, Mark, Model, Vehicle
from apps.security.models import User
from apps.security.serializers import UserDefaultSerializer


class DataOwnerSerializer(serializers.Serializer):
    identification_number = serializers.CharField(max_length=50, required=True)
    name = serializers.CharField(max_length=100, required=True)
    last_name = serializers.CharField(max_length=100, required=True)
    rif = serializers.CharField(max_length=100, required=True)
    license = serializers.CharField(max_length=100, required=True)
    medical_certificate = serializers.BooleanField(required=True)

    class Meta:
        fields = ('way_to_pay', 'credit', 'credit_limit', 'credit_limit_value', 'shopping_cart', 'apply_discount',
                  'discount_rate', 'price_list_id', 'withholding_agent', 'coin', 'credit_days', 'discount_action',
                  'type_action',)


class BannerDefaultSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    image = serializers.SerializerMethodField(required=False, read_only=True)

    def get_image(self, obj: Banner):
        if obj.image and hasattr(obj.image, 'url'):
            image_url = obj.image.url
            return image_url
        else:
            return None

    class Meta:
        model = Banner
        fields = serializers.ALL_FIELDS


class BannerEditSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    image = serializers.ImageField(required=False)

    class Meta:
        model = Banner
        fields = serializers.ALL_FIELDS


class BranchOfficeDefaultSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    number = serializers.IntegerField(read_only=True)

    class Meta:
        model = BranchOffice
        fields = serializers.ALL_FIELDS


class PremiumCoverageSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    insured_amount = serializers.DecimalField(max_digits=50, decimal_places=2, default=0.0)
    cost = serializers.DecimalField(max_digits=50, decimal_places=2, default=0.0)

    class Meta:
        model = Premium
        fields = serializers.ALL_FIELDS


class CoveragePremiumSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    premium = serializers.SerializerMethodField(read_only=True)

    def get_premium(self, obj: Coverage):
        request = self.context.get("request")
        use = request.query_params.get('use', None)
        if use:
            try:
                premium = Premium.objects.get(coverage_id=obj.id, use_id=use)
                PremiumCoverageSerializer(premium).data
            except ObjectDoesNotExist:
                return None

        return None

    class Meta:
        model = Coverage
        fields = serializers.ALL_FIELDS


class PremiumUseSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    plan = serializers.PrimaryKeyRelatedField(
        queryset=Plan.objects.all(),
        required=True,
    )
    use = serializers.PrimaryKeyRelatedField(
        queryset=Use.objects.all(),
        required=True,
    )
    coverage = serializers.PrimaryKeyRelatedField(
        queryset=Use.objects.all(),
        required=True,
    )
    coverage_display = CoveragePremiumSerializer(read_only=True, source='coverage', exclude=['plans', 'premium'])
    insured_amount = serializers.DecimalField(max_digits=50, decimal_places=2, default=0.0)
    cost = serializers.DecimalField(max_digits=50, decimal_places=2, default=0.0)

    class Meta:
        model = Premium
        fields = serializers.ALL_FIELDS


class UseDefaultSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    premiums = PremiumUseSerializer(many=True, read_only=True, source="premium_set", exclude=['use'])

    class Meta:
        model = Use
        fields = serializers.ALL_FIELDS


class CoveragePlanSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    premium = serializers.SerializerMethodField(read_only=True)

    def get_premium(self, obj: Coverage):
        request = self.context.get("request")
        use = request.query_params.get('use', None)
        if use:
            try:
                premium = Premium.objects.get(coverage_id=obj.id, use_id=use)
                return PremiumCoverageSerializer(premium).data
            except ObjectDoesNotExist:
                return None

        return None

    class Meta:
        model = Coverage
        fields = serializers.ALL_FIELDS


class PlanDefaultSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    uses = serializers.PrimaryKeyRelatedField(
        queryset=Use.objects.all(), many=True, required=False
    )
    uses_display = UseDefaultSerializer(many=True, read_only=True, source="uses", exclude=['created', 'updated'])
    coverage = CoveragePlanSerializer(many=True, read_only=True, exclude=['plans'])

    class Meta:
        model = Plan
        fields = serializers.ALL_FIELDS


class CoverageDefaultSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    plans_display = PlanDefaultSerializer(many=True, read_only=True, source='plans')
    premiums = PremiumCoverageSerializer(many=True, read_only=True, source="premium_set")

    class Meta:
        model = Coverage
        fields = serializers.ALL_FIELDS


class PremiumDefaultSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    coverage = serializers.PrimaryKeyRelatedField(
        queryset=Coverage.objects.all(),
        required=True,
    )
    coverage_display = CoverageDefaultSerializer(read_only=True, source='coverage')
    use = serializers.PrimaryKeyRelatedField(
        queryset=Use.objects.all(),
        required=True,
    )
    use_display = UseDefaultSerializer(read_only=True, source='use')
    plan = serializers.PrimaryKeyRelatedField(
        queryset=Plan.objects.all(),
        required=True,
    )
    plan_display = PlanDefaultSerializer(read_only=True, source='plan')
    insured_amount = serializers.DecimalField(max_digits=50, decimal_places=2, default=0.0)
    cost = serializers.DecimalField(max_digits=50, decimal_places=2, default=0.0)

    class Meta:
        model = Premium
        fields = serializers.ALL_FIELDS


class MarkDefaultSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    class Meta:
        model = Mark
        fields = serializers.ALL_FIELDS


class ModelDefaultSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    mark = serializers.PrimaryKeyRelatedField(
        queryset=Mark.objects.all(),
        required=True,
    )
    mark_display = MarkDefaultSerializer(read_only=True, source='mark')

    class Meta:
        model = Model
        fields = serializers.ALL_FIELDS


class VehicleDefaultSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    use = serializers.PrimaryKeyRelatedField(
        queryset=Use.objects.all(),
        required=True
    )
    use_display = UseDefaultSerializer(read_only=True, source='use')
    model = serializers.PrimaryKeyRelatedField(
        queryset=Model.objects.all(),
        required=True
    )
    model_display = ModelDefaultSerializer(read_only=True, source='model')
    taker = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        required=False
    )
    taker_display = UserDefaultSerializer(read_only=True, source='taker')
    # serializers.HiddenField(default=serializers.CurrentUserDefault())
    info = DataOwnerSerializer(write_only=True)

    def create(self, validated_data):
        try:
            request = self.context.get("request")
            with transaction.atomic():
                taker = validated_data.get('taker', None)
                if taker is None:
                    validated_data['taker'] = request.user

                vehicle = super(VehicleDefaultSerializer, self).create(validated_data)
        except ValueError as e:
            raise serializers.ValidationError(detail={"error": e})
        return vehicle

    class Meta:
        model = Vehicle
        fields = serializers.ALL_FIELDS
