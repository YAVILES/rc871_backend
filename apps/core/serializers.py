# coding=utf-8
from decimal import Decimal

from constance import config
from constance.backends.database.models import Constance
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.db.models import Q, Count
from django_restql.mixins import DynamicFieldsMixin
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from apps.core.models import Banner, BranchOffice, Use, Plan, Coverage, Premium, Mark, Model, Vehicle, State, City, \
    Municipality, Policy, PolicyCoverage, HistoricalChangeRate, Location, Section
from apps.payment.models import Payment
from apps.security.models import User
from apps.security.serializers import UserDefaultSerializer


class BannerDefaultSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    image_display = serializers.SerializerMethodField(required=False, read_only=True)

    def get_image_display(self, obj: Banner):
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


class SectionDefaultSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    type_display = serializers.CharField(source='get_type_display', read_only=True)
    type = serializers.CharField(max_length=10, required=False)
    image = serializers.ImageField(required=False)
    shape = serializers.ImageField(required=False)
    icon = serializers.ImageField(required=False)
    image_display = serializers.SerializerMethodField(required=False, read_only=True)

    def get_image_display(self, obj: Section):
        if obj.image and hasattr(obj.image, 'url'):
            image_url = obj.image.url
            return image_url
        else:
            return None

    shape_display = serializers.SerializerMethodField(required=False, read_only=True)

    def get_shape_display(self, obj: Section):
        if obj.shape and hasattr(obj.shape, 'url'):
            shape_url = obj.shape.url
            return shape_url
        else:
            return None

    icon_display = serializers.SerializerMethodField(required=False, read_only=True)

    def get_icon_display(self, obj: Section):
        if obj.icon and hasattr(obj.icon, 'url'):
            icon_url = obj.icon.url
            return icon_url
        else:
            return None

    class Meta:
        model = Section
        fields = serializers.ALL_FIELDS


class BranchOfficeDefaultSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    number = serializers.IntegerField(read_only=True)

    class Meta:
        model = BranchOffice
        fields = serializers.ALL_FIELDS


class PremiumCoverageSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    insured_amount = serializers.DecimalField(max_digits=50, decimal_places=2, default=0.0)
    insured_amount_display = serializers.CharField(read_only=True)
    cost = serializers.DecimalField(max_digits=50, decimal_places=2, default=0.0)
    cost_display = serializers.CharField(read_only=True)
    insured_amount_change = serializers.DecimalField(max_digits=50, decimal_places=2, default=0.0, read_only=True)
    insured_amount_change_display = serializers.CharField(read_only=True)
    cost_change = serializers.DecimalField(max_digits=50, decimal_places=2, default=0.0, read_only=True)
    cost_change__display = serializers.CharField(read_only=True)

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
                return PremiumCoverageSerializer(
                    premium, exclude=['created', 'updated']
                ).data
            except ObjectDoesNotExist:
                return None

        return None

    class Meta:
        model = Coverage
        fields = ('id', 'default', 'description', 'premium', 'plans',)


class PlanForUseSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    code = serializers.CharField()
    description = serializers.CharField()

    class Meta:
        model = Plan
        fields = serializers.ALL_FIELDS


class PlanWithCoverageSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    coverage = serializers.SerializerMethodField(read_only=True)
    cost_total = serializers.SerializerMethodField(read_only=True)
    cost_total_display = serializers.SerializerMethodField(read_only=True)
    cost_total_change = serializers.SerializerMethodField(read_only=True)
    cost_total_change_display = serializers.SerializerMethodField(read_only=True)
    insured_amount_total = serializers.SerializerMethodField(read_only=True)
    insured_amount_total_display = serializers.SerializerMethodField(read_only=True)
    insured_amount_total_change = serializers.SerializerMethodField(read_only=True)
    insured_amount_total_change_display = serializers.SerializerMethodField(read_only=True)

    def get_coverage(self, obj: Plan):
        self.context['plan'] = obj.id
        return CoveragePlanSerializer(
            obj.coverage, many=True, read_only=True, exclude=['plans'], context=self.context
        ).data

    def get_cost_total(self, plan: Plan):
        request = self.context.get("request")
        use = request.query_params.get('use', None)
        total = 0
        if use and plan:
            query = plan.coverage_set.filter(
                Q(default=False) & Q(is_active=True) & Q(premium__use_id=use) &
                Q(premium__cost__isnull=False)
            )
            query_default = Coverage.objects.filter(
                Q(default=True) & Q(is_active=True) & Q(premium__use_id=use) & Q(premium__cost__isnull=False)
            )
            coverage_list = query_default.union(query)
            try:
                for coverage in coverage_list:
                    premium = Premium.objects.get(plan_id=plan.id, coverage_id=coverage.id, use_id=use)
                    total += premium.cost
                return Decimal(total)
            except ObjectDoesNotExist:
                return None

        return None

    def get_cost_total_display(self, plan: Plan):
        cost_total = self.get_cost_total(plan)
        if cost_total:
            return '{} {}'.format(settings.CURRENCY_FORMAT, cost_total)
        return '{} 0'.format(settings.CURRENCY_FORMAT)

    def get_cost_total_change(self, plan: Plan):
        cost_total = self.get_cost_total(plan)
        if cost_total:
            try:
                change_factor = Constance.objects.get(key="CHANGE_FACTOR").value
            except ObjectDoesNotExist:
                getattr(config, "CHANGE_FACTOR")
                change_factor = Constance.objects.get(key="CHANGE_FACTOR").value
            return float(format(cost_total * Decimal(change_factor), ".2f"))
        return None

    def get_cost_total_change_display(self, plan: Plan):
        cost_total_change = self.get_cost_total_change(plan)
        if cost_total_change:
            return '{} {}'.format(settings.CURRENCY_CHANGE_FORMAT, cost_total_change)
        return '{} 0'.format(settings.CURRENCY_CHANGE_FORMAT)

    def get_insured_amount_total(self, plan: Plan):
        request = self.context.get("request")
        use = request.query_params.get('use', None)
        total = 0
        if use and plan:
            query = plan.coverage_set.filter(
                Q(default=False) & Q(is_active=True) & Q(premium__use_id=use) &
                Q(premium__cost__isnull=False)
            )
            query_default = Coverage.objects.filter(
                Q(default=True) & Q(is_active=True) & Q(premium__use_id=use) & Q(premium__cost__isnull=False)
            )
            coverage_list = query_default.union(query)
            try:
                for coverage in coverage_list:
                    premium = Premium.objects.get(plan_id=plan.id, coverage_id=coverage.id, use_id=use)
                    total += premium.insured_amount
                return total
            except ObjectDoesNotExist:
                return None

        return None

    def get_insured_amount_total_display(self, plan: Plan):
        insured_amount_total = self.get_insured_amount_total(plan)
        if insured_amount_total:
            return '{} {}'.format(settings.CURRENCY_FORMAT, insured_amount_total)
        return '{} 0'.format(settings.CURRENCY_FORMAT)

    def get_insured_amount_total_change(self, plan: Plan):
        insured_amount_total = self.get_insured_amount_total(plan)
        if insured_amount_total:
            try:
                change_factor = Constance.objects.get(key="CHANGE_FACTOR").value
            except ObjectDoesNotExist:
                getattr(config, "CHANGE_FACTOR")
                change_factor = Constance.objects.get(key="CHANGE_FACTOR").value
            return float(format(insured_amount_total * Decimal(change_factor), ".2f"))
        return None

    def get_insured_amount_total_change_display(self, plan: Plan):
        insured_amount_total_change = self.get_insured_amount_total_change(plan)
        if insured_amount_total_change:
            return '{} {}'.format(settings.CURRENCY_CHANGE_FORMAT, insured_amount_total_change)
        return '{} 0'.format(settings.CURRENCY_CHANGE_FORMAT)

    class Meta:
        model = Plan
        fields = ('id', 'description', 'coverage', 'cost_total', 'cost_total_display', 'cost_total_change',
                  'cost_total_change_display', 'insured_amount_total', 'insured_amount_total_display',
                  'insured_amount_total_change', 'insured_amount_total_change_display',)


class PlanDefaultSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    uses = serializers.PrimaryKeyRelatedField(
        queryset=Use.objects.all(), many=True, required=False
    )
    uses_display = UseDefaultSerializer(many=True, read_only=True, source="uses", exclude=['created', 'updated'])
    coverage = CoveragePlanSerializer(many=True, read_only=True, exclude=['plans'])

    def validate(self, attrs):
        self.context['plan'] = attrs.get('id', None)
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
    taker = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(is_staff=False),
        required=False
    )
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
    insured_amount_display = serializers.CharField(read_only=True)
    insured_amount_change = serializers.DecimalField(max_digits=50, decimal_places=2)
    insured_amount_change_display = serializers.CharField(read_only=True)
    cost = serializers.DecimalField(max_digits=50, decimal_places=2)
    cost_display = serializers.CharField(read_only=True)
    cost_change = serializers.DecimalField(max_digits=50, decimal_places=2)
    cost_change_display = serializers.CharField(read_only=True)
    coverage_display = CoverageDefaultSerializer(read_only=True, source="coverage")

    class Meta:
        model = PolicyCoverage
        exclude = ('created', 'updated',)


class PolicyCoverageCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PolicyCoverage
        fields = ('coverage',)


class PolicyDefaultSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    created_by = serializers.HiddenField(default=serializers.CurrentUserDefault(), write_only=True)
    created_by_display = UserDefaultSerializer(read_only=True, source='created_by')
    taker = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(is_staff=False),
        required=False
    )
    taker_display = UserDefaultSerializer(read_only=True, source='taker')
    adviser = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(is_staff=True),
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
        many=True,
        required=False,
        allow_null=True
    )
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    type_display = serializers.CharField(source='get_type_display', read_only=True)
    action_display = serializers.CharField(source='get_action_display', read_only=True)
    total_amount = serializers.DecimalField(max_digits=50, decimal_places=2, default=0.0, read_only=True)
    total_amount_display = serializers.CharField(read_only=True)
    total_amount_change = serializers.DecimalField(max_digits=50, decimal_places=2, default=0.0, read_only=True)
    total_amount_change_display = serializers.CharField(read_only=True)
    total_insured_amount = serializers.DecimalField(max_digits=50, decimal_places=2, default=0.0, read_only=True)
    total_insured_amount_display = serializers.CharField(read_only=True)
    total_insured_amount_change = serializers.DecimalField(max_digits=50, decimal_places=2, default=0.0, read_only=True)
    total_insured_amount_change_display = serializers.CharField(read_only=True)
    created_formated = serializers.SerializerMethodField(read_only=True)
    due_date_formated = serializers.SerializerMethodField(read_only=True)

    def get_created_formated(self, obj: Policy):
        return obj.created.strftime("%Y-%m-%d")

    def get_due_date_formated(self, obj: Policy):
        if obj.due_date:
            return obj.due_date.strftime("%Y-%m-%d")
        return None

    def create(self, validated_data):
        try:
            with transaction.atomic():
                request = self.context.get('request')  # Se pusa si el usuario es vendedor
                user = request.user
                plan = validated_data.get('plan')
                coverage = validated_data.pop('coverage', None)
                vehicle = validated_data.get('vehicle')
                taker = validated_data.get('taker', None)

                if taker is None:
                    validated_data['taker'] = request.user

                if user.is_adviser:
                    adviser = user
                else:
                    try:
                        adviser_id = Constance.objects.get(key="ADVISER_DEFAULT_ID").value
                    except ObjectDoesNotExist:
                        getattr(config, "CHANGE_FACTOR")
                        adviser_id = Constance.objects.get(key="ADVISER_DEFAULT_ID").value
                    if adviser_id is None:
                        adviser = User.objects.web()
                    else:
                        adviser = User.objects.get(pk=adviser_id)

                use = vehicle.use
                try:
                    change_factor = Constance.objects.get(key="CHANGE_FACTOR").value
                except ObjectDoesNotExist:
                    getattr(config, "CHANGE_FACTOR")
                    change_factor = Constance.objects.get(key="CHANGE_FACTOR").value

                items = []

                policy = Policy.objects.create(
                    adviser=adviser,
                    change_factor=0.0 if change_factor is None else float(change_factor),
                    **validated_data
                )

                total_insured_amount = 0.0
                total_amount = 0.0

                if coverage:
                    coverage_list = coverage
                else:
                    query = plan.coverage_set.filter(
                        Q(default=False) & Q(is_active=True) & Q(premium__use_id=use.id) &
                        Q(premium__cost__isnull=False)
                    )
                    query_default = Coverage.objects.filter(
                        Q(default=True) & Q(is_active=True) & Q(premium__use_id=use.id) & Q(premium__cost__isnull=False)
                    )
                    coverage_list = query_default.union(query).order_by('default', 'created', )

                for item in coverage_list:
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


class HomeDataSerializer(serializers.ModelSerializer):
    number_branches = serializers.SerializerMethodField(read_only=True)
    number_clients = serializers.SerializerMethodField(read_only=True)
    number_pending_policies = serializers.SerializerMethodField(read_only=True)
    number_insured_vehicles = serializers.SerializerMethodField(read_only=True)
    pending_payments = serializers.SerializerMethodField(read_only=True)

    def get_number_branches(self, obj: User):
        return BranchOffice.objects.aggregate(quantity=Count('id')).get('quantity', 0)

    def get_number_clients(self, obj: User):
        if obj.is_superuser:
            return User.objects.filter(
                is_staff=False, is_superuser=False, is_adviser=False
            ).aggregate(number=Count('id')).get('number', 0)
        else:
            return Policy.objects.filter(
                created_by_id=obj.id, taker__is_staff=False, taker__is_superuser=False, taker__is_adviser=False
            ).values('taker_id').distinct().aggregate(number=Count('taker_id')).get('number', 0)

    def get_number_pending_policies(self, obj: User):
        if obj.is_superuser:
            return Policy.objects.filter(
                Q(status=Policy.PENDING_APPROVAL) | Q(status=Policy.OUTSTANDING)
            ).aggregate(number=Count('id')).get('number', 0)
        else:
            return Policy.objects.filter(
                Q(Q(status=Policy.PENDING_APPROVAL) | Q(status=Policy.OUTSTANDING)) & Q(created_by_id=obj.id)
            ).aggregate(number=Count('id')).get('number', 0)

    def get_number_insured_vehicles(self, obj: User):
        if obj.is_superuser:
            return Policy.objects.filter(
                Q(status=Policy.PASSED) | Q(status=Policy.EXPIRED)
            ).values('vehicle_id').distinct().aggregate(number=Count('vehicle_id')).get('number', 0)
        else:
            return Policy.objects.filter(
                Q(Q(status=Policy.PASSED) | Q(status=Policy.EXPIRED)) & Q(created_by_id=obj.id)
            ).values('vehicle_id').distinct().aggregate(number=Count('vehicle_id')).get('number', 0)

    def get_pending_payments(self, obj: User):
        if obj.is_superuser:
            return Payment.objects.filter(status=Payment.PENDING).aggregate(quantity=Count('id')).get('quantity', 0)
        else:
            return Payment.objects.filter(
                status=Payment.PENDING, user_id=obj.id
            ).aggregate(quantity=Count('id')).get('quantity', 0)

    class Meta:
        model = User
        fields = ('number_branches', 'number_clients', 'number_pending_policies', 'number_insured_vehicles',
                  'pending_payments',)


class PolicyForBranchOfficeSerializer(serializers.ModelSerializer):
    quantity = serializers.SerializerMethodField(read_only=True)

    def get_quantity(self, obj: BranchOffice):
        request = self.context.get("request")
        user = request.user
        if user.is_superuser:
            return Policy.objects.filter(
                created_by__branch_office_id=obj.id
            ).aggregate(quantity=Count('id')).get('quantity', 0)
        else:
            return Policy.objects.filter(
                created_by__branch_office_id=obj.id,
                created_by_id=user.id
            ).aggregate(quantity=Count('id')).get('quantity', 0)

    class Meta:
        model = BranchOffice
        fields = ('id', 'number', 'description', 'quantity',)
