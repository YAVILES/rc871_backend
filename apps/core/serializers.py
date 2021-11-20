# coding=utf-8
from django_restql.mixins import DynamicFieldsMixin
from rest_framework import serializers

from apps.core.models import Banner


class BannerDefaultSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    class Meta:
        model = Banner
        fields = serializers.ALL_FIELDS
