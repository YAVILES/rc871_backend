import tablib
from django.db import transaction
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

from apps.core.admin import BannerResource
from apps.core.models import Banner, BranchOffice
from apps.core.serializers import BannerDefaultSerializer, BannerEditSerializer, BranchOfficeDefaultSerializer
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