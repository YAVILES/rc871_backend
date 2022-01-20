from auditlog.models import LogEntry
from constance.backends.database.models import Constance
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django_celery_beat.models import PeriodicTask, IntervalSchedule
from django_celery_results.models import TaskResult
from django_restql.mixins import DynamicFieldsMixin
from rest_framework import serializers

from apps.security.serializers import UserDefaultSerializer


class ContendTypeDefaultSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    class Meta:
        model = ContentType
        fields = serializers.ALL_FIELDS


class ConstanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Constance
        fields = ('id', 'key', 'value')


class LogEntrySerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    action_display = serializers.CharField(source='get_action_display', read_only=True)
    content_type = ContendTypeDefaultSerializer(read_only=True, required=False)
    actor = UserDefaultSerializer()
    changes_dict = serializers.DictField()
    changes_str = serializers.CharField()

    class Meta:
        model = LogEntry
        fields = serializers.ALL_FIELDS


class PeriodicTaskDefaultSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    class Meta:
        model = PeriodicTask
        fields = serializers.ALL_FIELDS


class IntervalScheduleSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    class Meta:
        model = IntervalSchedule
        fields = serializers.ALL_FIELDS


class TaskResultDefaultSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    module = serializers.SerializerMethodField(read_only=True)

    def get_module(self, task: TaskResult):
        try:
            return PeriodicTask.objects.get(task=task.task_name).name
        except ObjectDoesNotExist:
            return None

    class Meta:
        model = TaskResult
        fields = serializers.ALL_FIELDS
