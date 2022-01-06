# coding=utf-8
from django_restql.mixins import DynamicFieldsMixin
from rest_framework import serializers

from apps.core.models import Banner


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
