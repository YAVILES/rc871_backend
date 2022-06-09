import tablib
from django.db import transaction
from django.utils.translation import ugettext_lazy as _
from django.http import FileResponse
from rest_framework import mixins

# Create your views here.
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, serializers
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.permissions import AllowAny
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from tablib import Dataset

from apps.payment.admin import BankResource
from apps.payment.models import Bank, Payment
from django_filters import rest_framework as filters
from rest_framework.response import Response

from apps.payment.serializers import BankDefaultSerializer, PaymentDefaultSerializer, PaymentEditSerializer


class BankFilter(filters.FilterSet):
    class Meta:
        model = Bank
        fields = ['code', 'description']


class BankViewSet(ModelViewSet):
    queryset = Bank.objects.all()
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_class = BankFilter
    serializer_class = BankDefaultSerializer
    search_fields = ['code', 'description']
    permission_classes = (AllowAny,)
    authentication_classes = []

    def get_queryset(self):
        coin = self.request.query_params.get('coin', None)
        queryset = self.queryset
        if coin:
            return queryset.filter(coins__contains=coin)
        return queryset

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
        dataset = BankResource().export()
        return Response(dataset.csv, status=status.HTTP_200_OK)

    @action(methods=['POST'], detail=False)
    def _import(self, request):
        try:
            resource = BankResource()
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


class PaymentFilter(filters.FilterSet):

    class Meta:
        model = Payment
        fields = ['number', 'status', 'bank_id', 'method', 'policy_id', 'user_id', 'amount']


class PaymentViewSet(
    mixins.CreateModelMixin, mixins.RetrieveModelMixin, mixins.UpdateModelMixin, mixins.ListModelMixin, GenericViewSet
):
    queryset = Payment.objects.all().order_by('-number')
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_class = PaymentFilter
    serializer_class = PaymentDefaultSerializer
    search_fields = ['number', 'status', 'bank__description', 'method', 'policy_id', 'user__description', 'amount']

    def get_serializer_class(self):
        if self.action in ['create', 'update']:
            return PaymentEditSerializer
        return self.serializer_class

    def paginate_queryset(self, queryset):
        """
        Return a single page of results, or `None` if pagination is disabled.
        """
        not_paginator = self.request.query_params.get('not_paginator', None)
        if self.paginator is None or not_paginator:
            return None
        return self.paginator.paginate_queryset(queryset, self.request, view=self)

    @action(detail=True, methods=['POST', ])
    @transaction.atomic()
    def reject(self, request, pk):
        payment = self.get_object()
        commentary = request.data.get('commentary', None)
        if payment.status != Payment.PENDING:
            raise serializers.ValidationError(
                detail={'error': [_("Este pago ya fue procesado, no es posible rechazarlo")]})
        else:
            payment.status = Payment.REJECTED
            if commentary:
                payment.commentary = commentary

            payment.save(update_fields=['status', 'commentary'])
            return Response(status=status.HTTP_200_OK)

    @action(detail=False, methods=['POST', ])
    @transaction.atomic()
    def approve_payments(self, request):
        payments = request.data.get('payments', None)
        try:
            if payments:
                for payment in Payment.objects.filter(id__in=payments):
                    payment.status = Payment.ACCEPTED
                    payment.save(update_fields=['status'])
            else:
                raise serializers.ValidationError(
                    detail={'error': _("Debe seleccionar al menos un pago")})
        except ValueError as e:
            raise serializers.ValidationError(detail={'error': _(e.__str__())})
        return Response(status=status.HTTP_200_OK)

    @action(methods=['GET'], detail=True)
    def download_archive(self, request, pk):
        payment = self.get_object()
        filename = payment.archive.path
        response = FileResponse(open(filename, 'rb'))
        return response

    @action(methods=['GET'], detail=False)
    def field_options(self, request):
        field = self.request.query_params.get('field', None)
        fields = self.request.query_params.getlist('fields', None)
        if fields:
            try:
                data = {}
                for field in fields:
                    data[field] = []
                    for c in Payment._meta.get_field(field).choices:
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
                for c in Payment._meta.get_field(field).choices:
                    choices.append({
                        "value": c[0],
                        "description": c[1]
                    })
                return Response(choices, status=status.HTTP_200_OK)
            except ValueError as e:
                return Response(e, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"error": "the field parameter is mandatory"}, status=status.HTTP_400_BAD_REQUEST)

    # @action(methods=['GET'], detail=False)
    # def export(self, request):
    #     dataset = PaymentResource().export()
    #     response = HttpResponse(content_type='application/vnd.ms-excel')
    #     response['Content-Disposition'] = 'attachment; filename=cobros.xlsx'
    #     response.write(dataset.xlsx)
    #     return response