# coding=utf-8
from constance.backends.database.models import Constance
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django_restql.mixins import DynamicFieldsMixin
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from apps.core.models import Banner, BranchOffice, Use, Plan, Coverage, Premium, Mark, Model, Vehicle, State, City, \
    Municipality, Policy, PolicyCoverage, HistoricalChangeRate
from apps.security.models import User
from apps.security.serializers import UserDefaultSerializer


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
    premiums = serializers.SerializerMethodField(read_only=True)

    def get_premiums(self, instance: Use):
        request = self.context.get("request")
        plans = instance.plan_set.all().values_list('id', flat=True)
        queryset = instance.premium_set.filter(plan_id__in=plans)
        plan = request.query_params.get('plan', None)
        if plan:
            _plan = Plan.objects.get(pk=plan)
            queryset = queryset.filter(
                plan_id=_plan.id, coverage_id__in=_plan.coverage.all().values_list('id', flat=True)
            )

        return PremiumUseSerializer(queryset, many=True).data

    class Meta:
        model = Use
        fields = serializers.ALL_FIELDS


class CoveragePlanSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    premium = serializers.SerializerMethodField(read_only=True)

    def get_premium(self, obj: Coverage):
        request = self.context.get("request")
        plan = self.context.get('plan', None)
        use = request.query_params.get('use', None)
        if use and plan:
            try:
                premium = Premium.objects.get(plan_id=plan, coverage_id=obj.id, use_id=use)
                return PremiumCoverageSerializer(premium).data
            except ObjectDoesNotExist:
                return None

        return None

    class Meta:
        model = Coverage
        fields = serializers.ALL_FIELDS


class PlanForUseSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    code = serializers.CharField()
    description = serializers.CharField()

    class Meta:
        model = Plan
        fields = serializers.ALL_FIELDS


class PlanDefaultSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    uses = serializers.PrimaryKeyRelatedField(
        queryset=Use.objects.all(), many=True, required=False
    )
    uses_display = UseDefaultSerializer(many=True, read_only=True, source="uses", exclude=['created', 'updated'])
    coverage = CoveragePlanSerializer(many=True, read_only=True, exclude=['plans'])

    def validate(self, attrs):
        self.context['plan'] = attrs.id
        return attrs

    class Meta:
        model = Plan
        fields = serializers.ALL_FIELDS


class CoverageDefaultSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    plans_display = PlanDefaultSerializer(many=True, read_only=True, source='plans')
    premiums = serializers.SerializerMethodField(read_only=True)

    def get_premiums(self, instance: Coverage):
        request = self.context.get("request")
        plans = instance.plans.all().values_list('id', flat=True)
        queryset = instance.premium_set.filter(plan_id__in=plans)
        plan = request.query_params.get('plan', None)
        if plan:
            queryset = queryset.filter(plan_id=plan)

        return PremiumUseSerializer(queryset, many=True).data

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
    taker = serializers.HiddenField(default=serializers.CurrentUserDefault())
    taker_display = UserDefaultSerializer(read_only=True, source='taker')
    serial_bodywork = serializers.CharField()
    serial_engine = serializers.CharField()
    license_plate = serializers.CharField()
    stalls = serializers.IntegerField(default=4)
    color = serializers.CharField()
    transmission = serializers.IntegerField(default=1)
    transmission_display = serializers.CharField(source='get_transmission_display', read_only=True)
    owner_name = serializers.CharField()
    owner_last_name = serializers.CharField()
    owner_identity_card_image = serializers.ImageField(required=False)
    owner_license = serializers.ImageField(required=True)
    owner_circulation_card = serializers.ImageField(required=True)
    owner_medical_certificate = serializers.ImageField(required=False)

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


class StateDefaultSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    number = serializers.IntegerField(read_only=True)

    class Meta:
        model = State
        fields = serializers.ALL_FIELDS


class CityDefaultSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    number = serializers.IntegerField(read_only=True)

    class Meta:
        model = City
        fields = serializers.ALL_FIELDS


class MunicipalityDefaultSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    number = serializers.IntegerField(read_only=True)

    class Meta:
        model = Municipality
        fields = serializers.ALL_FIELDS


class PolicyCoverageSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    number = serializers.IntegerField()
    insured_amount = serializers.DecimalField(max_digits=50, decimal_places=2)
    cost = serializers.DecimalField(max_digits=50, decimal_places=2)
    coverage_display = CoverageDefaultSerializer(read_only=True, source="coverage")

    class Meta:
        model = PolicyCoverage
        exclude = ('created', 'updated',)


class PolicyCoverageCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PolicyCoverage
        fields = ('coverage',)


class PolicyDefaultSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    taker = serializers.HiddenField(default=serializers.CurrentUserDefault())
    taker_display = UserDefaultSerializer(read_only=True, source='taker')
    adviser = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        required=False
    )
    adviser_display = UserDefaultSerializer(read_only=True, source='adviser')
    vehicle = serializers.PrimaryKeyRelatedField(
        queryset=Vehicle.objects.all()
    )
    vehicle_display = VehicleDefaultSerializer(read_only=True, source='vehicle')
    plan = serializers.PrimaryKeyRelatedField(
        queryset=Plan.objects.all(),
    )
    plan_display = PlanDefaultSerializer(read_only=True, source='plan')
    items = PolicyCoverageSerializer(many=True, read_only=True)
    coverage = serializers.PrimaryKeyRelatedField(
        queryset=Coverage.objects.all(),
        write_only=True,
        many=True
    )
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    type_display = serializers.CharField(source='get_type_display', read_only=True)

    def create(self, validated_data):
        try:
            with transaction.atomic():
                request = self.context.get('request')# Se pusa si el usuario es vendedor
                user = request.user
                plan = validated_data.get('plan')
                coverage = validated_data.pop('coverage')
                vehicle = validated_data.get('vehicle')
                adviser = validated_data.pop('adviser', None)
                if adviser is None:
                    adviser = User.objects.web()

                use = vehicle.use
                change_factor = Constance.objects.get(key="CHANGE_FACTOR").value

                items = []

                policy = Policy.objects.create(
                    adviser=adviser,
                    change_factor=0.0 if change_factor is None else float(change_factor),
                    **validated_data
                )

                total_insured_amount = 0.0
                total_amount = 0.0

                for item in coverage:
                    premium = Premium.objects.get(plan_id=plan.id, use_id=use.id, coverage_id=item.id)
                    items.append(
                        {
                            'coverage': item,
                            'insured_amount': premium.insured_amount,
                            'cost': premium.cost,
                        }
                    )
                    total_insured_amount += float(premium.insured_amount)
                    total_amount += float(premium.cost)

                _items = [
                    PolicyCoverage(policy_id=policy.id, **item) for item in items
                ]

                PolicyCoverage.objects.bulk_create(_items)

                policy.total_insured_amount = total_insured_amount
                policy.total_amount = total_amount
                policy.save(update_fields=['total_insured_amount', 'total_amount'])

                return policy

        except ValidationError as error:
            raise serializers.ValidationError(detail={"error": error.detail})

    class Meta:
        model = Policy
        fields = serializers.ALL_FIELDS


class HistoricalChangeRateDefaultSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    class Meta:
        model = HistoricalChangeRate
        fields = serializers.ALL_FIELDS
