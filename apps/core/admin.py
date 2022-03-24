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
        import_id_fields = ('description',)


class CityResource(ModelResource):

    def before_import_row(self, row, row_number=None, **kwargs):
        state = row.get('state', None)

        if not state:
            raise ValidationError("El codigo del estado es obligatorio")
        else:
            row['state'] = State.objects.get(number=state).id

        return row

    class Meta:
        model = City
        exclude = ('id', 'created', 'updated',)
        import_id_fields = ('description', 'state')


class MunicipalityResource(ModelResource):

    def before_import_row(self, row, row_number=None, **kwargs):
        city = row.get('city', None)

        if not city:
            raise ValidationError("El codigo de la ciudad es obligatorio")
        else:
            row['city'] = City.objects.get(number=city).id

        return row

    class Meta:
        model = Municipality
        exclude = ('id', 'created', 'updated',)
        import_id_fields = ('description', 'city')


@admin.register(Banner)
class BrandAdmin(admin.ModelAdmin):
    list_display = ('title', 'subtitle',)
