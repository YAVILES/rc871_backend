from django.contrib import admin
from django.core.exceptions import ValidationError
from import_export.resources import ModelResource

from apps.core.models import Banner, State, City, Municipality, Mark, Model


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


class MarkResource(ModelResource):

    class Meta:
        model = Mark
        exclude = ('id', 'created', 'updated',)
        import_id_fields = ('description',)


class ModelVehicleResource(ModelResource):

    def before_import_row(self, row, row_number=None, **kwargs):
        mark = row.get('mark', None)

        if not mark:
            raise ValidationError("La marca es obligatoria")
        else:
            _mark, created = Mark.objects.get_or_create(description=mark)
            row['mark'] = _mark.id

        return row

    class Meta:
        model = Model
        exclude = ('id', 'created', 'updated',)
        import_id_fields = ('mark', 'description',)


@admin.register(Banner)
class BrandAdmin(admin.ModelAdmin):
    list_display = ('title', 'subtitle',)
