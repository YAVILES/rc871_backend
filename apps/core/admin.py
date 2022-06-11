from datetime import datetime
from import_export.fields import Field

from django.contrib import admin
from django.core.exceptions import ValidationError, ObjectDoesNotExist, MultipleObjectsReturned
from import_export.resources import ModelResource
from import_export.widgets import ForeignKeyWidget

from apps.core.models import Banner, State, City, Municipality, Mark, Model, HistoricalChangeRate, Use, Vehicle
from apps.security.models import User


class BannerResource(ModelResource):
    title = Field(attribute='title', column_name='Titulo')
    subtitle = Field(attribute='subtitle', column_name='Sub Titulo')
    content = Field(attribute='content', column_name='Contenido')
    url = Field(attribute='url', column_name='Url')
    sequence_order = Field(attribute='sequence_order', column_name='Secuencia')
    is_active = Field(attribute='is_active', column_name='Activo')

    class Meta:
        model = Banner
        exclude = ('id', 'created', 'updated', 'image',)
        import_id_fields = ('title',)


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
    description = Field(attribute='description', column_name='Descripcion')
    is_active = Field(attribute='is_active', column_name='Activo')

    class Meta:
        model = Mark
        exclude = ('id', 'created', 'updated',)
        import_id_fields = ('description',)


class ModelVehicleResource(ModelResource):
    mark = Field(
        attribute='mark', widget=ForeignKeyWidget(Mark, 'description'), column_name='Marca'
    )
    description = Field(attribute='description', column_name='Descripcion')
    is_active = Field(attribute='is_active', column_name='Activo')

    class Meta:
        model = Model
        exclude = ('id', 'created', 'updated',)
        import_id_fields = ('mark', 'description',)


class VehicleResource(ModelResource):
    use = Field(
        attribute='use', widget=ForeignKeyWidget(Use, 'description'), column_name='Uso'
    )
    model = Field(
        attribute='model', widget=ForeignKeyWidget(Model, 'description'), column_name='Modelo'
    )
    license_plate = Field(attribute='license_plate', column_name='Placa')
    serial_bodywork = Field(attribute='serial_bodywork', column_name='Serial de Carroceria')
    serial_engine = Field(attribute='serial_engine', column_name='Serial de Motor')
    stalls = Field(attribute='stalls', column_name='Nro. de Asientos')
    color = Field(attribute='color', column_name='Color')
    year = Field(attribute='year', column_name='Año')
    transmission = Field(attribute='get_transmission_display', column_name='Transmision')
    owner_name = Field(attribute='owner_name', column_name='Nombre del dueño')
    owner_last_name = Field(attribute='owner_last_name', column_name='Apellido del dueño')
    owner_identity_card = Field(attribute='owner_identity_card', column_name='CI del dueño')
    owner_phones = Field(attribute='owner_phones', column_name='Telefonos del dueño')
    owner_address = Field(attribute='owner_address', column_name='Direccion del dueño')
    owner_email = Field(attribute='owner_email', column_name='Correo del dueño')
    taker = Field(attribute='taker', widget=ForeignKeyWidget(User, 'username'), column_name='Tomador', readonly=True)
    is_active = Field(attribute='is_active', column_name='Activo')

    class Meta:
        model = Vehicle
        exclude = ('id', 'created', 'updated', 'owner_identity_card_image', 'owner_license',
                   'owner_medical_certificate', 'owner_circulation_card',)
        import_id_fields = ('license_plate',)


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


