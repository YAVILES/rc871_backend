from datetime import datetime

import tablib
from auditlog.models import LogEntry
from constance.backends.database.models import Constance
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django_celery_results.models import TaskResult
from django_filters import rest_framework as filters
from django.db import transaction
from django_celery_beat.models import PeriodicTask, IntervalSchedule
from django_filters.rest_framework import DjangoFilterBackend
from money.currency import Currency, CurrencyHelper
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from tablib import Dataset

from apps.system.serializers import ConstanceSerializer, IntervalScheduleSerializer, LogEntrySerializer, \
    PeriodicTaskDefaultSerializer, TaskResultDefaultSerializer
from rc871_backend.utils.functions import get_settings, format_headers_import


class ConfigurationFilter(filters.FilterSet):
    class Meta:
        model = Constance
        fields = ['key']


class ConfigurationViewSet(ModelViewSet):
    queryset = Constance.objects.all()
    serializer_class = ConstanceSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = ConfigurationFilter
    paginator = None

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        value = request.data.get('value', None)
        instance.value = value
        instance.save()
        return Response(ConstanceSerializer(instance).data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['PUT', ])
    @transaction.atomic()
    def update_multiple(self, request):
        for item in request.data:
            instance = Constance.objects.get(key=item.get('key'))
            instance.value = item.get('value', None)
            instance.save(update_fields=['value'])
        return Response(request.data, status=status.HTTP_200_OK)

    def list(self, request, *args, **kwargs):
        """
             get all setting item
        """
        allow_settings = [key for key, options in getattr(
            settings, 'CONSTANCE_CONFIG', {}).items()]
        items = get_settings(allow_settings)
        return Response(items, status=status.HTTP_200_OK)

    @action(methods=['GET', ], detail=False)
    def retrieve_for_key(self, request):
        key = self.request.query_params.get('key', None)
        if key:
            instance = Constance.objects.get(key=key)
            data = {
                'id': str(instance.id),
                'key': instance.key,
                'value': instance.value
            }
            return Response(data)
        else:
            return Response({"error": "el key es obligatorio"}, status=status.HTTP_404_NOT_FOUND)


class IntervalScheduleViewSet(ModelViewSet):
    queryset = IntervalSchedule.objects.all()
    serializer_class = IntervalScheduleSerializer

    @action(methods=['GET'], detail=False)
    def field_options(self, request):
        field = self.request.query_params.get('field', None)
        fields = self.request.query_params.getlist('fields', None)
        if fields:
            try:
                data = {}
                for field in fields:
                    data[field] = []
                    for c in IntervalSchedule._meta.get_field(field).choices:
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
                for c in IntervalSchedule._meta.get_field(field).choices:
                    choices.append({
                        "value": c[0],
                        "description": c[1]
                    })
                return Response(choices, status=status.HTTP_200_OK)
            except ValueError as e:
                return Response(e, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"error": "the field parameter is mandatory"}, status=status.HTTP_400_BAD_REQUEST)


class LogViewSet(ReadOnlyModelViewSet):
    queryset = LogEntry.objects.all()
    serializer_class = LogEntrySerializer
    filter_backends = [DjangoFilterBackend, SearchFilter]
    search_fields = ['id', 'object_repr', 'timestamp',  'changes', 'actor__email', 'actor__name', 'actor__last_name',
                     'content_type__app_label', 'content_type__model']


class InfoAPIView(APIView):
    permission_classes = (AllowAny,)
    authentication_classes = []

    def get(self, request, format=None):
        return Response({
            'version': settings.SITE_VERSION,
            'logo': settings.SITE_LOGO,
            'name': settings.SITE_NAME
        }, status=status.HTTP_200_OK)


class PeriodicTaskViewSet(ModelViewSet):
    queryset = PeriodicTask.objects.all()
    serializer_class = PeriodicTaskDefaultSerializer


class TaskResultFilter(filters.FilterSet):
    module = filters.CharFilter(method="get_module")

    class Meta:
        model = TaskResult
        fields = ['id', 'task_name', 'status', 'result']

    def get_module(self, queryset, name, value):
        if value:
            return queryset.filter(accounts__mobile_payment_applies=True)
        return queryset


class TaskResultViewSet(ModelViewSet):
    queryset = TaskResult.objects.all()
    serializer_class = TaskResultDefaultSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_class = TaskResultFilter
    search_fields = ['id', 'task_name', 'status']

    def paginate_queryset(self, queryset):
        """
        Return a single page of results, or `None` if pagination is disabled.
        """
        not_paginator = self.request.query_params.get('not_paginator', None)

        if not_paginator:
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
                    for c in TaskResult._meta.get_field(field).choices:
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
                for c in TaskResult._meta.get_field(field).choices:
                    choices.append({
                        "value": c[0],
                        "description": c[1]
                    })
                return Response(choices, status=status.HTTP_200_OK)
            except ValueError as e:
                return Response(e, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"error": "the field parameter is mandatory"}, status=status.HTTP_400_BAD_REQUEST)

