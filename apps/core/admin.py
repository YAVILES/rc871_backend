from datetime import datetime

from django.contrib import admin
from django.core.exceptions import ValidationError, ObjectDoesNotExist, MultipleObjectsReturned
from import_export.resources import ModelResource

from apps.core.models import Banner, State, City, Municipality, Mark, Model, HistoricalChangeRate


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


class HistoricalChangeRateResource(ModelResource):

    def skip_row(self, instance, original):
        if not original.id:
            return False
        try:
            doc: HistoricalChangeRate = HistoricalChangeRate.objects.get(
                id=instance.id
            )
            doc.rate = instance.rate
            doc.save(update_fields=["rate"])

        except ObjectDoesNotExist:
            try:
                doc: HistoricalChangeRate = HistoricalChangeRate.objects.get(
                    valid_from=instance.valid_from,
                    valid_until=instance.valid_until
                )
                doc.rate = instance.rate
                doc.save(update_fields=["rate"])
                return True
            except MultipleObjectsReturned:
                HistoricalChangeRate.objects.filter(
                    valid_from=instance.valid_from,
                    valid_until=instance.valid_until
                ).delete()
                return False
            except ObjectDoesNotExist:
                return False

    def before_import_row(self, row, row_number=None, **kwargs):
        validodesde = row.get('validodesde', None)
        validohasta = row.get('validohasta', None)
        tasa = row.get('tasa', None)
        if validodesde:
            row['valid_from'] = validodesde
        else:
            valid_from = row.get('valid_from', None)
            if valid_from:
                _valid_from = datetime(int(str(valid_from)[0:4]), int(str(valid_from)[4:6]), int(str(valid_from)[6:8]))
                row['valid_from'] = _valid_from.date()
            else:
                raise ValidationError("La fecha desde es obligatoria")

        if validohasta:
            row['valid_until'] = validohasta
        else:
            valid_until = row.get('valid_until', None)
            if valid_until:
                _valid_until = datetime(int(str(valid_until)[0:4]), int(str(valid_until)[4:6]),
                                        int(str(valid_until)[6:8]))
                row['valid_until'] = _valid_until.date()
            else:
                raise ValidationError("La fecha hasta es obligatoria")

        if tasa:
            rate = tasa
            row['rate'] = tasa
        else:
            rate = row.get('rate', None)

        if not rate:
            raise ValidationError("La tasa es obligatoria")
        return row

    class Meta:
        model = HistoricalChangeRate
        fields = ('id', 'valid_from', 'valid_until', 'rate',)


@admin.register(Banner)
class BrandAdmin(admin.ModelAdmin):
    list_display = ('title', 'subtitle',)


