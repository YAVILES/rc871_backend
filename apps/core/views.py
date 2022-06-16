import io
from os import path, remove

import pdfkit
import qrcode
import tablib
from django.conf import settings
from django.core.files import File
from django.core.files.images import ImageFile
from django.db import transaction
from django.db.models import Q
from django.http import FileResponse, HttpResponse
from django.template.loader import render_to_string
from django_filters.rest_framework import DjangoFilterBackend
from money.currency import Currency, CurrencyHelper
from rest_framework import status, serializers
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from six import BytesIO
from tablib import Dataset
from django_filters import rest_framework as filters
from django.utils.translation import ugettext_lazy as _

from apps.core.admin import BannerResource, StateResource, CityResource, MunicipalityResource, MarkResource, \
    ModelVehicleResource, HistoricalChangeRateResource, VehicleResource, BranchOfficeResource, UseResource, \
    PlanResource, CoverageResource, PremiumResource, PolicyResource
from apps.core.models import Banner, BranchOffice, Use, Plan, Coverage, Premium, Mark, Model, Vehicle, State, City, \
    Municipality, Policy, HistoricalChangeRate, file_policy_path, Section
from apps.core.serializers import BannerDefaultSerializer, BannerEditSerializer, BranchOfficeDefaultSerializer, \
    UseDefaultSerializer, PlanDefaultSerializer, CoverageDefaultSerializer, PremiumDefaultSerializer, \
    ModelDefaultSerializer, MarkDefaultSerializer, VehicleDefaultSerializer, MunicipalityDefaultSerializer, \
    CityDefaultSerializer, StateDefaultSerializer, PolicyDefaultSerializer, HistoricalChangeRateDefaultSerializer, \
    PlanWithCoverageSerializer, HomeDataSerializer, PolicyForBranchOfficeSerializer, SectionDefaultSerializer


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
        response = HttpResponse(content_type='application/vnd.ms-excel')
        response['Content-Disposition'] = 'attachment; filename=banners.xlsx'
        response.write(dataset.xlsx)
        return response

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


class SectionFilter(filters.FilterSet):
    class Meta:
        model = Section
        fields = ['title', 'subtitle', 'content', 'url', 'sequence_order', 'is_active']


class SectionViewSet(ModelViewSet):
    queryset = Section.objects.all()
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_class = SectionFilter
    serializer_class = SectionDefaultSerializer
    search_fields = ['title', 'subtitle', 'content', 'url', 'sequence_order', 'is_active']
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

    @action(methods=['GET'], detail=False)
    def field_options(self, request):
        field = self.request.query_params.get('field', None)
        fields = self.request.query_params.getlist('fields', None)
        if fields:
            try:
                data = {}
                for field in fields:
                    data[field] = []
                    for c in Section._meta.get_field(field).choices:
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
                for c in Section._meta.get_field(field).choices:
                    choices.append({
                        "value": c[0],
                        "description": c[1]
                    })
                return Response(choices, status=status.HTTP_200_OK)
            except ValueError as e:
                return Response(e, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"error": "the field parameter is mandatory"}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['DELETE', ])
    @transaction.atomic()
    def remove_multiple(self, request):
        ids = request.data.get('ids', None)
        try:
            if ids:
                Section.objects.filter(id__in=ids).delete()
            else:
                raise serializers.ValidationError(
                    detail={'error': _("Debe seleccionar al menos una sección")})
        except ValueError as e:
            raise serializers.ValidationError(detail={'error': _(e.__str__())})
        return Response(status=status.HTTP_200_OK)


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

    @action(methods=['GET'], detail=False)
    def export(self, request):
        dataset = BranchOfficeResource().export()
        response = HttpResponse(content_type='application/vnd.ms-excel')
        response['Content-Disposition'] = 'attachment; filename=sucursales.xlsx'
        response.write(dataset.xlsx)
        return response

    @action(methods=['POST'], detail=False)
    def _import(self, request):
        try:
            resource = BranchOfficeResource()
            errors = []
            invalids = []
            if request.FILES:
                file = request.FILES['file']
                data_set = Dataset()
                data_set.load(file.read())
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

    @action(methods=['GET'], detail=False)
    def export(self, request):
        dataset = UseResource().export()
        response = HttpResponse(content_type='application/vnd.ms-excel')
        response['Content-Disposition'] = 'attachment; filename=usos.xlsx'
        response.write(dataset.xlsx)
        return response

    @action(methods=['POST'], detail=False)
    def _import(self, request):
        try:
            resource = UseResource()
            errors = []
            invalids = []
            if request.FILES:
                file = request.FILES['file']
                data_set = Dataset()
                data_set.load(file.read())
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


class PlanFilter(filters.FilterSet):
    use = filters.UUIDFilter(method="verified_use")

    def verified_use(self, queryset, name, value):
        if value:
            queryset = queryset.filter(
                Q(uses__in=[value]) & Q(coverage__premium__use_id=value) & Q(coverage__premium__cost__gt=0)
            ).distinct()
        return queryset

    class Meta:
        model = Plan
        fields = ['code', 'description', 'is_active', 'use']


class PlanViewSet(ModelViewSet):
    queryset = Plan.objects.all()
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_class = PlanFilter
    serializer_class = PlanDefaultSerializer
    search_fields = ['code', 'description', 'is_active']
    permission_classes = (AllowAny,)
    authentication_classes = []

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve'] and self.request.query_params.get('use', None):
            return PlanWithCoverageSerializer
        return self.serializer_class

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
        dataset = PlanResource().export()
        response = HttpResponse(content_type='application/vnd.ms-excel')
        response['Content-Disposition'] = 'attachment; filename=planes.xlsx'
        response.write(dataset.xlsx)
        return response

    @action(methods=['POST'], detail=False)
    def _import(self, request):
        try:
            resource = PlanResource()
            errors = []
            invalids = []
            if request.FILES:
                file = request.FILES['file']
                data_set = Dataset()
                data_set.load(file.read())
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

    @action(methods=['GET'], detail=False)
    def export(self, request):
        dataset = CoverageResource().export()
        response = HttpResponse(content_type='application/vnd.ms-excel')
        response['Content-Disposition'] = 'attachment; filename=coberturas.xlsx'
        response.write(dataset.xlsx)
        return response

    @action(methods=['POST'], detail=False)
    def _import(self, request):
        try:
            resource = CoverageResource()
            errors = []
            invalids = []
            if request.FILES:
                file = request.FILES['file']
                data_set = Dataset()
                data_set.load(file.read())
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

    @action(methods=['GET'], detail=False)
    def export(self, request):
        dataset = PremiumResource().export()
        response = HttpResponse(content_type='application/vnd.ms-excel')
        response['Content-Disposition'] = 'attachment; filename=coberturas.xlsx'
        response.write(dataset.xlsx)
        return response

    @action(methods=['POST'], detail=False)
    def _import(self, request):
        try:
            resource = PremiumResource()
            errors = []
            invalids = []
            if request.FILES:
                file = request.FILES['file']
                data_set = Dataset()
                data_set.load(file.read())
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


class MarkFilter(filters.FilterSet):
    class Meta:
        model = Mark
        fields = ['description']


class MarkViewSet(ModelViewSet):
    queryset = Mark.objects.all()
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_class = MarkFilter
    serializer_class = MarkDefaultSerializer
    search_fields = ['description']
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

    @action(methods=['GET'], detail=False)
    def export(self, request):
        dataset = MarkResource().export()
        response = HttpResponse(content_type='application/vnd.ms-excel')
        response['Content-Disposition'] = 'attachment; filename=marcas.xlsx'
        response.write(dataset.xlsx)
        return response


class ModelFilter(filters.FilterSet):
    class Meta:
        model = Model
        fields = ['mark', 'description', 'mark__description']


class ModelVehicleViewSet(ModelViewSet):
    queryset = Model.objects.all()
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_class = ModelFilter
    serializer_class = ModelDefaultSerializer
    search_fields = ['description', 'mark__description']
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

    @action(methods=['GET'], detail=False)
    def export(self, request):
        dataset = ModelVehicleResource().export()
        response = HttpResponse(content_type='application/vnd.ms-excel')
        response['Content-Disposition'] = 'attachment; filename=modelos.xlsx'
        response.write(dataset.xlsx)
        return response


class VehicleFilter(filters.FilterSet):
    class Meta:
        model = Vehicle
        fields = ['serial_bodywork', 'serial_engine', 'license_plate', 'transmission', 'taker__username',
                  'model__description', 'taker_id', 'use_id']


class VehicleViewSet(ModelViewSet):
    queryset = Vehicle.objects.all()
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_class = VehicleFilter
    serializer_class = VehicleDefaultSerializer
    search_fields = ['serial_bodywork', 'serial_engine', 'license_plate', 'transmission', 'taker__username',
                     'model__description', 'use_id', 'taker_id']
    permission_classes = (AllowAny,)

    def get_queryset(self):
        queryset = self.queryset
        user = self.request.user

        if user.is_superuser:
            return queryset

        if not user.is_staff:
            return queryset.filter(taker_id=user.id)

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
                elif archive == 'owner_circulation_card':
                    filename = vehicle.owner_circulation_card.path
                elif archive == 'registration_certificate':
                    filename = vehicle.registration_certificate.path
                elif archive == 'holder_s_license':
                    filename = vehicle.holder_s_license.path
                elif archive == 'medical_certificate':
                    filename = vehicle.medical_certificate.path
                else:
                    return Response(
                        {"error": "Debe identificar que archivo desea descargar"},
                        status=status.HTTP_400_BAD_REQUEST
                    )
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

    @action(methods=['POST'], detail=False)
    def _import(self, request):
        try:
            resource = VehicleResource()
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

    @action(methods=['GET'], detail=False)
    def export(self, request):
        dataset = VehicleResource().export()
        response = HttpResponse(content_type='application/vnd.ms-excel')
        response['Content-Disposition'] = 'attachment; filename=modelos.xlsx'
        response.write(dataset.xlsx)
        return response


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


class PolicyFilter(filters.FilterSet):
    class Meta:
        model = Policy
        fields = ['number', 'taker__name', 'adviser__name', 'vehicle__model__mark__description',
                  'vehicle__model__description']


class PolicyViewSet(ModelViewSet):
    queryset = Policy.objects.all()
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_class = PolicyFilter
    serializer_class = PolicyDefaultSerializer
    search_fields = ['number', 'taker__name', 'adviser__name', 'vehicle__model__mark__description',
                     'vehicle__model__description']

    def get_queryset(self):
        queryset = self.queryset
        user = self.request.user

        if user.is_superuser:
            return queryset

        if user.is_staff:
            return queryset.filter(adviser_id=user.id)
        else:
            return queryset.filter(taker_id=user.id)

    def paginate_queryset(self, queryset):
        """
        Return a single page of results, or `None` if pagination is disabled.
        """
        not_paginator = self.request.query_params.get('not_paginator', None)
        if self.paginator is None or not_paginator:
            return None
        return self.paginator.paginate_queryset(queryset, self.request, view=self)

    @action(methods=['GET'], detail=True)
    def pdf(self, request, pk):
        policy = self.get_object()
        if policy.status == Policy.PASSED:
            if policy.file and path.exists(policy.file.path):
                remove(policy.file.path)
            if policy.qrcode and path.exists(policy.qrcode.path):
                remove(policy.qrcode.path)

            data = file_policy_path(policy, '{0}.pdf'.format(str(policy.number)))
            img = qrcode.make(settings.MEDIA_URL + data)
            buf = BytesIO()  # BytesIO se da cuenta de leer y escribir bytes en la memoria
            img.save(buf)
            image_stream = buf.getvalue()
            qr_image = ImageFile(io.BytesIO(image_stream), name='qrcode.png')
            policy.qrcode = qr_image
            policy.save(update_fields=['qrcode'])
            context = PolicyDefaultSerializer(policy, context=self.get_serializer_context()).data
            html = render_to_string("report-pdf.html", context)
            pdf = pdfkit.from_string(html, False)
            pdf_file = File(io.BytesIO(pdf), name='{0}.pdf'.format(str(policy.number)))
            policy.file = pdf_file
            policy.save()
            response = HttpResponse(pdf, content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; filename="policy.pdf"'
        else:
            raise serializers.ValidationError(
                detail={'error': _("La poliza {0} no esta aprobada".format(policy.number))})

        return response

    @action(methods=['GET'], detail=True)
    def download_pdf(self, request, pk):
        policy = self.get_object()
        if policy.status == Policy.PASSED:
            if policy.file and path.exists(policy.file.path):
                filename = policy.file.path
                response = FileResponse(open(filename, 'rb'))
            else:
                if policy.qrcode and path.exists(policy.qrcode.path):
                    remove(policy.qrcode.path)

                data = file_policy_path(policy, '{0}.pdf'.format(str(policy.number)))
                img = qrcode.make(settings.MEDIA_URL + data)
                buf = BytesIO()  # BytesIO se da cuenta de leer y escribir bytes en la memoria
                img.save(buf)
                image_stream = buf.getvalue()
                qr_image = ImageFile(io.BytesIO(image_stream), name='qrcode.png')
                policy.qrcode = qr_image
                policy.save(update_fields=['qrcode'])
                context = PolicyDefaultSerializer(policy, context=self.get_serializer_context()).data
                html = render_to_string("report-pdf.html", context)
                pdf = pdfkit.from_string(html, False)
                pdf_file = File(io.BytesIO(pdf), name='{0}.pdf'.format(str(policy.number)))
                policy.file = pdf_file
                policy.save()
                response = HttpResponse(pdf, content_type='application/pdf')
                response['Content-Disposition'] = 'attachment; filename="policy.pdf"'
        else:
            raise serializers.ValidationError(
                detail={'error': _("La poliza {0} no esta aprobada".format(policy.number))})
        return response

    @action(methods=['GET'], detail=False)
    def export(self, request):
        dataset = PolicyResource().export()
        response = HttpResponse(content_type='application/vnd.ms-excel')
        response['Content-Disposition'] = 'attachment; filename=polizas.xlsx'
        response.write(dataset.xlsx)
        return response


class HistoricalChangeRateFilter(filters.FilterSet):
    min_valid_from = filters.DateFilter(field_name="valid_from", lookup_expr='gte')
    max_valid_from = filters.DateFilter(field_name="valid_from", lookup_expr='lte')
    min_valid_until = filters.DateFilter(field_name="valid_until", lookup_expr='gte')
    max_valid_until = filters.DateFilter(field_name="valid_until", lookup_expr='lte')
    min_rate = filters.NumberFilter(field_name="rate", lookup_expr='gte')
    max_rate = filters.NumberFilter(field_name="rate", lookup_expr='lte')

    class Meta:
        model = HistoricalChangeRate
        fields = ['rate', 'min_valid_from', 'max_valid_from', 'min_valid_until', 'max_valid_until']


class HistoricalChangeRateViewSet(ModelViewSet):
    queryset = HistoricalChangeRate.objects.all().order_by('-valid_from')
    serializer_class = HistoricalChangeRateDefaultSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_class = HistoricalChangeRateFilter
    search_fields = ['rate', 'valid_from', 'valid_until']

    def paginate_queryset(self, queryset):
        """
        Return a single page of results, or `None` if pagination is disabled.
        """
        not_paginator = self.request.query_params.get('not_paginator', None)

        if not_paginator:
            return None
        return self.paginator.paginate_queryset(queryset, self.request, view=self)

    @action(methods=['POST'], detail=False)
    def _import(self, request):
        try:
            resource = HistoricalChangeRateResource()
            errors = []
            invalids = []
            if request.FILES:
                file = request.FILES['file']
                data_set = Dataset()
                data_set.load(file.read())
                result = resource.import_data(
                    data_set, dry_run=True)  # Test the data import
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
                result = resource.import_data(
                    data_set, dry_run=False)  # Actually import now
                return Response({
                    "totals": result.totals,
                    "total_rows": result.total_rows,
                }, status=status.HTTP_200_OK)
        except ValueError as e:
            return Response(e, status=status.HTTP_400_BAD_REQUEST)


class CoinAPIView(APIView):
    permission_classes = (AllowAny,)
    authentication_classes = []

    def get(self, request):
        return Response([
            {
                'value': coin.value,
                'description': CurrencyHelper._CURRENCY_DATA[coin]['display_name']
            } for coin in settings.COINS
        ], status=status.HTTP_200_OK)


class HomeDataAPIView(GenericViewSet):
    permission_classes = (AllowAny,)

    def get_serializer_class(self):
        if self.action == 'data':
            return HomeDataSerializer
        if self.action == 'policy_for_branch_office':
            return PolicyForBranchOfficeSerializer

    @action(methods=['GET', ], detail=False)
    def data(self, request):
        data = HomeDataSerializer(self.request.user).data
        return Response(data, status=status.HTTP_200_OK)

    @action(methods=['GET', ], detail=False)
    def policy_for_branch_office(self, request):
        data = PolicyForBranchOfficeSerializer(
            BranchOffice.objects.filter(is_active=True),
            context=self.get_serializer_context(),
            many=True
        ).data
        return Response(data, status=status.HTTP_200_OK)
