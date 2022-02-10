# coding=utf-8
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django_restql.mixins import DynamicFieldsMixin
from rest_framework import serializers

from apps.core.models import Banner, BranchOffice, Use, Plan, Coverage, Premium, Mark, Model, Vehicle
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
    taker = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        required=False
    )
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

    owner_rif = serializers.ImageField(required=False)

    def get_owner_rif(self, obj: 'Vehicle'):
        if obj.owner_rif and hasattr(obj.owner_rif, 'url'):
            owner_rif_url = obj.owner_rif.url
            return owner_rif_url
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

    registration_certificate = serializers.ImageField(required=False)

    def get_registration_certificate(self, obj: 'Vehicle'):
        if obj.registration_certificate and hasattr(obj.registration_certificate, 'url'):
            registration_certificate_url = obj.registration_certificate.url
            return registration_certificate_url
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
    # serializers.HiddenField(default=serializers.CurrentUserDefault())

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
