# coding=utf-8
from constance.backends.database.models import Constance
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django_restql.mixins import DynamicFieldsMixin
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
    taker = serializers.HiddenField(default=serializers.CurrentUserDefault())
    taker_display = UserDefaultSerializer(read_only=True, source='taker')
    serial_bodywork = serializers.CharField()
    serial_engine = serializers.CharField()
    license_plate = serializers.CharField()
    stalls = serializers.IntegerField(default=4)
    color = serializers.CharField()
    transmission = serializers.IntegerField()
    transmission_display = serializers.CharField(source='get_transmission_display', read_only=True)
    owner_name = serializers.CharField()
    owner_last_name = serializers.CharField()
    owner_identity_card = serializers.ImageField(required=False)

    def get_owner_identity_card(self, obj: 'Vehicle'):
        if obj.owner_identity_card and hasattr(obj.owner_identity_card, 'url'):
            owner_identity_card_url = obj.owner_identity_card.url
            return owner_identity_card_url
        else:
            return None

    owner_license = serializers.ImageField(required=False)

    def get_owner_license(self, obj: 'Vehicle'):
        if obj.owner_license and hasattr(obj.owner_license, 'url'):
            owner_license_url = obj.owner_license.url
            return owner_license_url
        else:
            return None

    owner_medical_certificate = serializers.ImageField(required=False)

    def get_owner_medical_certificate(self, obj: 'Vehicle'):
        if obj.owner_medical_certificate and hasattr(obj.owner_medical_certificate, 'url'):
            owner_medical_certificate_url = obj.owner_medical_certificate.url
            return owner_medical_certificate_url
        else:
            return None

    circulation_card = serializers.ImageField(required=False)

    def get_circulation_card(self, obj: 'Vehicle'):
        if obj.circulation_card and hasattr(obj.circulation_card, 'url'):
            circulation_card_url = obj.circulation_card.url
            return circulation_card_url
        else:
            return None

    holder_s_license = serializers.ImageField(required=False)

    def get_holder_s_license(self, obj: 'Vehicle'):
        if obj.holder_s_license and hasattr(obj.holder_s_license, 'url'):
            holder_s_license_url = obj.holder_s_license.url
            return holder_s_license_url
        else:
            return None

    medical_certificate = serializers.ImageField(required=False)

    def get_medical_certificate(self, obj: 'Vehicle'):
        if obj.medical_certificate and hasattr(obj.medical_certificate, 'url'):
            medical_certificate_url = obj.medical_certificate.url
            return medical_certificate_url
        else:
            return None

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
    change_factor = serializers.DecimalField(max_digits=50, decimal_places=2)

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
        write_only=True,
        required=False
    )
    adviser_display = UserDefaultSerializer(read_only=True, source='adviser')
    vehicle = serializers.PrimaryKeyRelatedField(
        queryset=Vehicle.objects.all(),
        write_only=True,
    )
    vehicle_display = VehicleDefaultSerializer(read_only=True, source='vehicle')
    plan = serializers.PrimaryKeyRelatedField(
        queryset=Plan.objects.all(),
        write_only=True,
    )
    plan_display = PlanDefaultSerializer(read_only=True, source='plan')
    items = PolicyCoverageSerializer(many=True, read_only=True)
    coverage = serializers.PrimaryKeyRelatedField(
        queryset=Coverage.objects.all(),
        write_only=True,
        many=True
    )
    status_display = serializers.CharField(source='get_status_display', read_only=True)

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
                    **validated_data
                )

                for item in coverage:
                    premium = Premium.objects.get(plan_id=plan.id, use_id=use.id, coverage_id=item.id)
                    items.append(
                        {
                            'coverage': item,
                            'insured_amount': premium.insured_amount,
                            'cost': premium.cost,
                            'change_factor': 0.0 if change_factor is None else float(change_factor)
                        }
                    )

                _items = [
                    PolicyCoverage(policy_id=policy.id, **item) for item in items
                ]

                PolicyCoverage.objects.bulk_create(_items)

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
