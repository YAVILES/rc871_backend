import tablib
from django.db import transaction
from django.http import FileResponse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, serializers, mixins
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from tablib import Dataset
from django_filters import rest_framework as filters
from django.utils.translation import ugettext_lazy as _

from apps.core.admin import BannerResource, StateResource, CityResource, MunicipalityResource, MarkResource, \
    ModelVehicleResource
from apps.core.models import Banner, BranchOffice, Use, Plan, Coverage, Premium, Mark, Model, Vehicle, State, City, \
    Municipality
from apps.core.serializers import BannerDefaultSerializer, BannerEditSerializer, BranchOfficeDefaultSerializer, \
    UseDefaultSerializer, PlanDefaultSerializer, CoverageDefaultSerializer, PremiumDefaultSerializer, \
    ModelDefaultSerializer, MarkDefaultSerializer, VehicleDefaultSerializer, MunicipalityDefaultSerializer, \
    CityDefaultSerializer, StateDefaultSerializer
from rc871_backend.utils.functions import format_headers_import


class BannerFilter(filters.FilterSet):
    class Meta:
        model = Banner
        fields = ['title', 'subtitle', 'content', 'url', 'sequence_order', 'is_active']


class BannerViewSet(ModelViewSet):
    queryset = Banner.objects.all()
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_class = BannerFilter
    serializer_class = BannerDefaultSerializer
    search_fields = ['title', 'subtitle', 'content', 'url', 'sequence_order', 'is_active']
    permission_classes = (AllowAny,)
    authentication_classes = []

    def get_serializer_class(self):
        if self.action in ['create', 'update']:
            return BannerEditSerializer
        return self.serializer_class

    def paginate_queryset(self, queryset):
        """
        Return a single page of results, or `None` if pagination is disabled.
        """
        not_paginator = self.request.query_params.get('not_paginator', None)
        if self.paginator is None or not_paginator:
            return None
        return self.paginator.paginate_queryset(queryset, self.request, view=self)

    @action(detail=False, methods=['DELETE', ])
    @transaction.atomic()
    def remove_multiple(self, request):
        ids = request.data.get('ids', None)
        try:
            if ids:
                Banner.objects.filter(id__in=ids).delete()
            else:
                raise serializers.ValidationError(
                    detail={'error': _("Debe seleccionar al menos un banner")})
        except ValueError as e:
            raise serializers.ValidationError(detail={'error': _(e.__str__())})
        return Response(status=status.HTTP_200_OK)

    @action(methods=['GET'], detail=False)
    def export(self, request):
        dataset = BannerResource().export()
        return Response(dataset.csv, status=status.HTTP_200_OK)

    @action(methods=['POST'], detail=False)
    def _import(self, request):
        try:
            resource = BannerResource()
            errors = []
            invalids = []
            if request.FILES:
                file = request.FILES['file']
                data_set = Dataset()
                data_set.load(file.read())
                data_set.headers = format_headers_import(data_set.headers)
                result = resource.import_data(data_set, dry_run=True)  # Test the data import
            else:
                headers = request.data['headers']
                data_set = tablib.Dataset(headers=headers)
                for d in request.data['data']:
                    data_set.append(d)
                result = resource.import_data(data_set, dry_run=True)

            if result.has_errors() or len(result.invalid_rows) > 0:
                for row in result.invalid_rows:
                    invalids.append(
                        {
                            "row": row.number + 1,
                            "error": row.error,
                            "error_dict": row.error_dict,
                            "values": row.values
                        }
                    )

                for row in result.row_errors():
                    err = row[1]
                    errors.append(
                        {
                            "errors": [e.error.__str__() for e in err],
                            "values": err[0].row,
                            "row": row[0]
                        }
                    )

                return Response({
                    "rows_error": errors,
                    "invalid_rows": invalids,
                    "totals": result.totals,
                    "total_rows": result.total_rows,
                }, status=status.HTTP_400_BAD_REQUEST)
            else:
                result = resource.import_data(data_set, dry_run=False)  # Actually import now
                return Response({
                    "totals": result.totals,
                    "total_rows": result.total_rows,
                }, status=status.HTTP_200_OK)
        except ValueError as e:
            return Response(e, status=status.HTTP_400_BAD_REQUEST)


class BranchOfficeFilter(filters.FilterSet):
    class Meta:
        model = BranchOffice
        fields = ['number', 'code', 'description', 'is_active']


class BranchOfficeViewSet(ModelViewSet):
    queryset = BranchOffice.objects.all()
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_class = BranchOfficeFilter
    serializer_class = BranchOfficeDefaultSerializer
    search_fields = ['number', 'code', 'description', 'is_active']
    permission_classes = (AllowAny,)

    def paginate_queryset(self, queryset):
        """
        Return a single page of results, or `None` if pagination is disabled.
        """
        not_paginator = self.request.query_params.get('not_paginator', None)
        if self.paginator is None or not_paginator:
            return None
        return self.paginator.paginate_queryset(queryset, self.request, view=self)


class UseFilter(filters.FilterSet):
    class Meta:
        model = Use
        fields = ['code', 'description', 'is_active']


class UseViewSet(ModelViewSet):
    queryset = Use.objects.all()
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_class = UseFilter
    serializer_class = UseDefaultSerializer
    search_fields = ['code', 'description', 'is_active']
    permission_classes = (AllowAny,)
    authentication_classes = []

    def paginate_queryset(self, queryset):
        """
        Return a single page of results, or `None` if pagination is disabled.
        """
        not_paginator = self.request.query_params.get('not_paginator', None)
        if self.paginator is None or not_paginator:
            return None
        return self.paginator.paginate_queryset(queryset, self.request, view=self)


class PlanFilter(filters.FilterSet):
    class Meta:
        model = Plan
        fields = ['code', 'description', 'is_active']


class PlanViewSet(ModelViewSet):
    queryset = Plan.objects.all()
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_class = PlanFilter
    serializer_class = PlanDefaultSerializer
    search_fields = ['code', 'description', 'is_active']
    permission_classes = (AllowAny,)
    authentication_classes = []

    def paginate_queryset(self, queryset):
        """
        Return a single page of results, or `None` if pagination is disabled.
        """
        not_paginator = self.request.query_params.get('not_paginator', None)
        if self.paginator is None or not_paginator:
            return None
        return self.paginator.paginate_queryset(queryset, self.request, view=self)


class CoverageFilter(filters.FilterSet):
    class Meta:
        model = Coverage
        fields = ['code', 'description', 'is_active']


class CoverageViewSet(ModelViewSet):
    queryset = Coverage.objects.all()
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_class = CoverageFilter
    serializer_class = CoverageDefaultSerializer
    search_fields = ['code', 'description', 'is_active']
    permission_classes = (AllowAny,)

    def paginate_queryset(self, queryset):
        """
        Return a single page of results, or `None` if pagination is disabled.
        """
        not_paginator = self.request.query_params.get('not_paginator', None)
        if self.paginator is None or not_paginator:
            return None
        return self.paginator.paginate_queryset(queryset, self.request, view=self)


class PremiumFilter(filters.FilterSet):
    class Meta:
        model = Premium
        fields = ['coverage', 'use', 'insured_amount', 'cost']


class PremiumViewSet(ModelViewSet):
    queryset = Premium.objects.all()
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_class = PremiumFilter
    serializer_class = PremiumDefaultSerializer
    search_fields = ['coverage', 'use', 'insured_amount', 'cost']
    permission_classes = (AllowAny,)

    def paginate_queryset(self, queryset):
        """
        Return a single page of results, or `None` if pagination is disabled.
        """
        not_paginator = self.request.query_params.get('not_paginator', None)
        if self.paginator is None or not_paginator:
            return None
        return self.paginator.paginate_queryset(queryset, self.request, view=self)

    @action(detail=False, methods=['POST', ])
    @transaction.atomic()
    def multiple(self, request):
        premiums = request.data.get('premiums', None)
        try:
            if premiums:
                for premium in premiums:
                    obj, created = Premium.objects.update_or_create(
                        coverage_id=premium['coverage'],
                        use_id=premium['use'],
                        plan_id=premium['plan'],
                        defaults={
                            'insured_amount': premium['insured_amount'],
                            'cost': premium['cost'],
                        },
                    )
            else:
                raise serializers.ValidationError(
                    detail={'error': _("Debe enviar al menos una prima")})
        except ValueError as e:
            raise serializers.ValidationError(detail={'error': _(e.__str__())})
        return Response(status=status.HTTP_200_OK)


class MarkFilter(filters.FilterSet):
    class Meta:
        model = Mark
        fields = ['code', 'description']


class MarkViewSet(ModelViewSet):
    queryset = Mark.objects.all()
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_class = MarkFilter
    serializer_class = MarkDefaultSerializer
    search_fields = ['code', 'description']
    permission_classes = (AllowAny,)

    def paginate_queryset(self, queryset):
        """
        Return a single page of results, or `None` if pagination is disabled.
        """
        not_paginator = self.request.query_params.get('not_paginator', None)
        if self.paginator is None or not_paginator:
            return None
        return self.paginator.paginate_queryset(queryset, self.request, view=self)

    @action(methods=['POST'], detail=False)
    def _import(self, request):
        try:
            resource = MarkResource()
            errors = []
            invalids = []
            if request.FILES:
                file = request.FILES['file']
                data_set = Dataset()
                data_set.load(file.read())
                data_set.headers = data_set.headers
                result = resource.import_data(data_set, dry_run=True)  # Test the data import
            else:
                headers = request.data['headers']
                data_set = tablib.Dataset(headers=headers)
                for d in request.data['data']:
                    data_set.append(d)
                result = resource.import_data(data_set, dry_run=True)

            if result.has_errors() or len(result.invalid_rows) > 0:
                for row in result.invalid_rows:
                    invalids.append(
                        {
                            "row": row.number + 1,
                            "error": row.error,
                            "error_dict": row.error_dict,
                            "values": row.values
                        }
                    )

                for row in result.row_errors():
                    err = row[1]
                    errors.append(
                        {
                            "errors": [e.error.__str__() for e in err],
                            "values": err[0].row,
                            "row": row[0]
                        }
                    )

                return Response({
                    "rows_error": errors,
                    "invalid_rows": invalids,
                    "totals": result.totals,
                    "total_rows": result.total_rows,
                }, status=status.HTTP_400_BAD_REQUEST)
            else:
                result = resource.import_data(data_set, dry_run=False)  # Actually import now
                return Response({
                    "totals": result.totals,
                    "total_rows": result.total_rows,
                }, status=status.HTTP_200_OK)
        except ValueError as e:
            return Response(e, status=status.HTTP_400_BAD_REQUEST)


class ModelFilter(filters.FilterSet):
    class Meta:
        model = Model
        fields = ['code', 'mark', 'description', 'mark__description']


class ModelViewSet(ModelViewSet):
    queryset = Model.objects.all()
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_class = ModelFilter
    serializer_class = ModelDefaultSerializer
    search_fields = ['code', 'mark', 'description', 'mark__description']
    permission_classes = (AllowAny,)

    def paginate_queryset(self, queryset):
        """
        Return a single page of results, or `None` if pagination is disabled.
        """
        not_paginator = self.request.query_params.get('not_paginator', None)
        if self.paginator is None or not_paginator:
            return None
        return self.paginator.paginate_queryset(queryset, self.request, view=self)

    @action(methods=['POST'], detail=False)
    def _import(self, request):
        try:
            resource = ModelVehicleResource()
            errors = []
            invalids = []
            if request.FILES:
                file = request.FILES['file']
                data_set = Dataset()
                data_set.load(file.read())
                data_set.headers = data_set.headers
                result = resource.import_data(data_set, dry_run=True)  # Test the data import
            else:
                headers = request.data['headers']
                data_set = tablib.Dataset(headers=headers)
                for d in request.data['data']:
                    data_set.append(d)
                result = resource.import_data(data_set, dry_run=True)

            if result.has_errors() or len(result.invalid_rows) > 0:
                for row in result.invalid_rows:
                    invalids.append(
                        {
                            "row": row.number + 1,
                            "error": row.error,
                            "error_dict": row.error_dict,
                            "values": row.values
                        }
                    )

                for row in result.row_errors():
                    err = row[1]
                    errors.append(
                        {
                            "errors": [e.error.__str__() for e in err],
                            "values": err[0].row,
                            "row": row[0]
                        }
                    )

                return Response({
                    "rows_error": errors,
                    "invalid_rows": invalids,
                    "totals": result.totals,
                    "total_rows": result.total_rows,
                }, status=status.HTTP_400_BAD_REQUEST)
            else:
                result = resource.import_data(data_set, dry_run=False)  # Actually import now
                return Response({
                    "totals": result.totals,
                    "total_rows": result.total_rows,
                }, status=status.HTTP_200_OK)
        except ValueError as e:
            return Response(e, status=status.HTTP_400_BAD_REQUEST)


class VehicleFilter(filters.FilterSet):
    class Meta:
        model = Vehicle
        fields = ['serial_bodywork', 'serial_engine', 'license_plate', 'transmission', 'taker__username',
                  'model__description']


class VehicleViewSet(ModelViewSet):
    queryset = Vehicle.objects.all()
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_class = VehicleFilter
    serializer_class = VehicleDefaultSerializer
    search_fields = ['serial_bodywork', 'serial_engine', 'license_plate', 'transmission', 'taker__username',
                     'model__description']
    permission_classes = (AllowAny,)

    @action(methods=['GET'], detail=True)
    def download_archive(self, request, pk):
        archive = self.request.query_params.get('archive', None)
        if archive:
            vehicle: Vehicle = self.get_object()
            try:
                if archive == 'owner_identity_card':
                    filename = vehicle.owner_identity_card.path
                elif archive == 'owner_rif':
                    filename = vehicle.owner_rif.path
                elif archive == 'owner_license':
                    filename = vehicle.owner_license.path
                elif archive == 'owner_medical_certificate':
                    filename = vehicle.owner_medical_certificate.path
                elif archive == 'circulation_card':
                    filename = vehicle.circulation_card.path
                elif archive == 'registration_certificate':
                    filename = vehicle.registration_certificate.path
                elif archive == 'holder_s_license':
                    filename = vehicle.holder_s_license.path
                elif archive == 'medical_certificate':
                    filename = vehicle.medical_certificate.path
                response = FileResponse(open(filename, 'rb'))
                return response
            except ValueError as e:
                return Response(
                    {"error": e.__str__()},
                    status=status.HTTP_400_BAD_REQUEST
                )
        else:
            return Response(
                {"error": "Debe identificar que archivo desea descargar"},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(methods=['GET'], detail=False)
    def field_options(self, request):
        field = self.request.query_params.get('field', None)
        fields = self.request.query_params.getlist('fields', None)
        if fields:
            try:
                data = {}
                for field in fields:
                    data[field] = []
                    for c in Vehicle._meta.get_field(field).choices:
                        data[field].append({
                            "value": c[0],
                            "description": c[1]
                        })
                return Response(data, status=status.HTTP_200_OK)
            except ValueError as e:
                return Response(e, status=status.HTTP_400_BAD_REQUEST)
        elif field:
            try:
                choices = []
                for c in Vehicle._meta.get_field(field).choices:
                    choices.append({
                        "value": c[0],
                        "description": c[1]
                    })
                return Response(choices, status=status.HTTP_200_OK)
            except ValueError as e:
                return Response(e, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"error": "the field parameter is mandatory"}, status=status.HTTP_400_BAD_REQUEST)

    def paginate_queryset(self, queryset):
        """
        Return a single page of results, or `None` if pagination is disabled.
        """
        not_paginator = self.request.query_params.get('not_paginator', None)
        if self.paginator is None or not_paginator:
            return None
        return self.paginator.paginate_queryset(queryset, self.request, view=self)


class StateFilter(filters.FilterSet):
    class Meta:
        model = State
        fields = ['description', 'number']


class StateViewSet(ModelViewSet):
    queryset = State.objects.all()
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_class = StateFilter
    serializer_class = StateDefaultSerializer
    search_fields = ['description', 'number']
    permission_classes = (AllowAny,)

    def paginate_queryset(self, queryset):
        """
        Return a single page of results, or `None` if pagination is disabled.
        """
        not_paginator = self.request.query_params.get('not_paginator', None)
        if self.paginator is None or not_paginator:
            return None
        return self.paginator.paginate_queryset(queryset, self.request, view=self)

    @action(methods=['GET'], detail=False)
    def export(self, request):
        dataset = StateResource().export()
        return Response(dataset.csv, status=status.HTTP_200_OK)

    @action(methods=['POST'], detail=False)
    def _import(self, request):
        try:
            resource = StateResource()
            errors = []
            invalids = []
            if request.FILES:
                file = request.FILES['file']
                data_set = Dataset()
                data_set.load(file.read())
                data_set.headers = data_set.headers
                result = resource.import_data(data_set, dry_run=True)  # Test the data import
            else:
                headers = request.data['headers']
                data_set = tablib.Dataset(headers=headers)
                for d in request.data['data']:
                    data_set.append(d)
                result = resource.import_data(data_set, dry_run=True)

            if result.has_errors() or len(result.invalid_rows) > 0:
                for row in result.invalid_rows:
                    invalids.append(
                        {
                            "row": row.number + 1,
                            "error": row.error,
                            "error_dict": row.error_dict,
                            "values": row.values
                        }
                    )

                for row in result.row_errors():
                    err = row[1]
                    errors.append(
                        {
                            "errors": [e.error.__str__() for e in err],
                            "values": err[0].row,
                            "row": row[0]
                        }
                    )

                return Response({
                    "rows_error": errors,
                    "invalid_rows": invalids,
                    "totals": result.totals,
                    "total_rows": result.total_rows,
                }, status=status.HTTP_400_BAD_REQUEST)
            else:
                result = resource.import_data(data_set, dry_run=False)  # Actually import now
                return Response({
                    "totals": result.totals,
                    "total_rows": result.total_rows,
                }, status=status.HTTP_200_OK)
        except ValueError as e:
            return Response(e, status=status.HTTP_400_BAD_REQUEST)


class CityFilter(filters.FilterSet):
    class Meta:
        model = City
        fields = ['description', 'number', 'state__description', 'state_id']


class CityViewSet(ModelViewSet):
    queryset = City.objects.all()
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_class = CityFilter
    serializer_class = CityDefaultSerializer
    search_fields = ['description', 'number', 'state__description']
    permission_classes = (AllowAny,)

    def paginate_queryset(self, queryset):
        """
        Return a single page of results, or `None` if pagination is disabled.
        """
        not_paginator = self.request.query_params.get('not_paginator', None)
        if self.paginator is None or not_paginator:
            return None
        return self.paginator.paginate_queryset(queryset, self.request, view=self)

    @action(methods=['GET'], detail=False)
    def export(self, request):
        dataset = CityResource().export()
        return Response(dataset.csv, status=status.HTTP_200_OK)

    @action(methods=['POST'], detail=False)
    def _import(self, request):
        try:
            resource = CityResource()
            errors = []
            invalids = []
            if request.FILES:
                file = request.FILES['file']
                data_set = Dataset()
                data_set.load(file.read())
                data_set.headers = data_set.headers
                result = resource.import_data(data_set, dry_run=True)  # Test the data import
            else:
                headers = request.data['headers']
                data_set = tablib.Dataset(headers=headers)
                for d in request.data['data']:
                    data_set.append(d)
                result = resource.import_data(data_set, dry_run=True)

            if result.has_errors() or len(result.invalid_rows) > 0:
                for row in result.invalid_rows:
                    invalids.append(
                        {
                            "row": row.number + 1,
                            "error": row.error,
                            "error_dict": row.error_dict,
                            "values": row.values
                        }
                    )

                for row in result.row_errors():
                    err = row[1]
                    errors.append(
                        {
                            "errors": [e.error.__str__() for e in err],
                            "values": err[0].row,
                            "row": row[0]
                        }
                    )

                return Response({
                    "rows_error": errors,
                    "invalid_rows": invalids,
                    "totals": result.totals,
                    "total_rows": result.total_rows,
                }, status=status.HTTP_400_BAD_REQUEST)
            else:
                result = resource.import_data(data_set, dry_run=False)  # Actually import now
                return Response({
                    "totals": result.totals,
                    "total_rows": result.total_rows,
                }, status=status.HTTP_200_OK)
        except ValueError as e:
            return Response(e, status=status.HTTP_400_BAD_REQUEST)


class MunicipalityFilter(filters.FilterSet):
    class Meta:
        model = Municipality
        fields = ['description', 'number', 'city__state__description', 'city__description', 'city_id', 'city__state_id']


class MunicipalityViewSet(ModelViewSet):
    queryset = Municipality.objects.all()
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_class = MunicipalityFilter
    serializer_class = MunicipalityDefaultSerializer
    search_fields = ['description', 'number', 'city__state__description', 'city__description']
    permission_classes = (AllowAny,)

    def paginate_queryset(self, queryset):
        """
        Return a single page of results, or `None` if pagination is disabled.
        """
        not_paginator = self.request.query_params.get('not_paginator', None)
        if self.paginator is None or not_paginator:
            return None
        return self.paginator.paginate_queryset(queryset, self.request, view=self)

    @action(methods=['GET'], detail=False)
    def export(self, request):
        dataset = MunicipalityResource().export()
        return Response(dataset.csv, status=status.HTTP_200_OK)

    @action(methods=['POST'], detail=False)
    def _import(self, request):
        try:
            resource = MunicipalityResource()
            errors = []
            invalids = []
            if request.FILES:
                file = request.FILES['file']
                data_set = Dataset()
                data_set.load(file.read())
                data_set.headers = data_set.headers
                result = resource.import_data(data_set, dry_run=True)  # Test the data import
            else:
                headers = request.data['headers']
                data_set = tablib.Dataset(headers=headers)
                for d in request.data['data']:
                    data_set.append(d)
                result = resource.import_data(data_set, dry_run=True)

            if result.has_errors() or len(result.invalid_rows) > 0:
                for row in result.invalid_rows:
                    invalids.append(
                        {
                            "row": row.number + 1,
                            "error": row.error,
                            "error_dict": row.error_dict,
                            "values": row.values
                        }
                    )

                for row in result.row_errors():
                    err = row[1]
                    errors.append(
                        {
                            "errors": [e.error.__str__() for e in err],
                            "values": err[0].row,
                            "row": row[0]
                        }
                    )

                return Response({
                    "rows_error": errors,
                    "invalid_rows": invalids,
                    "totals": result.totals,
                    "total_rows": result.total_rows,
                }, status=status.HTTP_400_BAD_REQUEST)
            else:
                result = resource.import_data(data_set, dry_run=False)  # Actually import now
                return Response({
                    "totals": result.totals,
                    "total_rows": result.total_rows,
                }, status=status.HTTP_200_OK)
        except ValueError as e:
            return Response(e, status=status.HTTP_400_BAD_REQUEST)
