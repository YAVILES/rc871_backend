from django.contrib import admin
from import_export.resources import ModelResource

from apps.core.models import Banner, State, City, Municipality


class BannerResource(ModelResource):
    class Meta:
        model = Banner
        exclude = ('id', 'created', 'updated',)


class StateResource(ModelResource):
    class Meta:
        model = State
        exclude = ('id', 'created', 'updated',)


@admin.register(Banner)
class BrandAdmin(admin.ModelAdmin):
    list_display = ('title', 'subtitle',)
