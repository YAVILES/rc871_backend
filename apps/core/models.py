import uuid
from os import remove
from os import path
from sequences import get_next_value

from django.db import models, IntegrityError
from django.utils.translation import ugettext_lazy as _

MONDAY = 0
TUESDAY = 1
WEDNESDAY = 2
THURSDAY = 3
FRIDAY = 4
SATURDAY = 5
SUNDAY = 6

DAYS = (
    (MONDAY, _('Lunes')),
    (TUESDAY, _('Martes')),
    (WEDNESDAY, _('Miercoles')),
    (THURSDAY, _('Jueves')),
    (FRIDAY, _('Viernes')),
    (SATURDAY, _('Sábado')),
    (SUNDAY, _('Domingo')),
)


class ModelBase(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    created = models.DateTimeField(verbose_name=_('created'), auto_now_add=True)
    updated = models.DateTimeField(verbose_name=_('updated'), auto_now=True)

    class Meta:
        abstract = True


class Location(ModelBase):
    description = models.CharField(max_length=100, verbose_name=_('description'))
    last_sync_date = models.DateTimeField(null=True, blank=True, verbose_name=_('last sync date'))

    def __str__(self):
        return self.description if not self.parent else "{} -> {}".format(self.description, self.parent.description)

    class Meta:
        verbose_name = _('location')
        verbose_name_plural = _('locations')
        ordering = ['description']


def banner_image_path(product: 'Banner', file_name):
    return 'img/banner/{0}/{1}'.format(product.title, file_name)


class Banner(ModelBase):
    title = models.CharField(max_length=100, verbose_name=_('title'))
    subtitle = models.CharField(max_length=100, verbose_name=_('subtitle'))
    content = models.CharField(max_length=255, verbose_name=_('content'))
    image = models.ImageField(upload_to='photos/', null=True, verbose_name=_('image'))
    url = models.CharField(max_length=255, verbose_name=_('url'))
    sequence_order = models.IntegerField(verbose_name='sequence order', default=1)
    is_active = models.BooleanField(verbose_name=_('is active'), default=True)

    def delete(self, using=None, keep_parents=False):
        models.signals.pre_delete.send(sender=self.__class__,
                                       instance=self,
                                       using=using)
        image_path = None
        if self.image and hasattr(self.image, 'url'):
            image_path = self.image.path
        if image_path and path.exists(image_path):
            remove(image_path)
        Banner.objects.filter(pk=self.id).delete()
        models.signals.post_delete.send(sender=self.__class__,
                                        instance=self,
                                        using=using)

    class Meta:
        verbose_name = _('banner')
        verbose_name_plural = _('banners')
        ordering = ['sequence_order']


def get_branch_office_number():
    return get_next_value('branch_office_number')


class BranchOffice(ModelBase):
    number = models.PositiveIntegerField(verbose_name='number', primary_key=False, db_index=True,
                                         default=get_branch_office_number)
    code = models.CharField(max_length=50, blank=True, null=True, verbose_name=_('code'))
    description = models.CharField(max_length=100, verbose_name=_('description'))
    is_active = models.BooleanField(verbose_name=_('is active'), default=True)
    last_sync_date = models.DateTimeField(null=True, blank=True, verbose_name=_('last sync date'))

    def __str__(self):
        return self.description

    class Meta:
        verbose_name = _('branch office')
        verbose_name_plural = _('branch offices')
        ordering = ['number']


class Use(ModelBase):
    code = models.CharField(max_length=50, blank=True, null=True, verbose_name=_('code'))
    description = models.CharField(max_length=100, verbose_name=_('description'))
    is_active = models.BooleanField(verbose_name=_('is active'), default=True)
    last_sync_date = models.DateTimeField(null=True, blank=True, verbose_name=_('last sync date'))

    def __str__(self):
        return self.description

    class Meta:
        verbose_name = _('use')
        verbose_name_plural = _('uses')
        ordering = ['code']


class Plan(ModelBase):
    code = models.CharField(max_length=50, blank=True, null=True, verbose_name=_('code'))
    description = models.CharField(max_length=100, verbose_name=_('description'))
    uses = models.ManyToManyField(
        Use,
        verbose_name=_('uses'),
        blank=True,
    )
    is_active = models.BooleanField(verbose_name=_('is active'), default=True)
    last_sync_date = models.DateTimeField(null=True, blank=True, verbose_name=_('last sync date'))

    @property
    def coverage(self):
        query = self.coverage_set.all()
        query_default = Coverage.objects.filter(default=True)
        return query_default.union(query)

    def __str__(self):
        return self.description

    class Meta:
        verbose_name = _('plan')
        verbose_name_plural = _('plans')
        ordering = ['code']


class Coverage(ModelBase):
    code = models.CharField(max_length=50, blank=True, null=True, verbose_name=_('code'))
    description = models.CharField(max_length=100, verbose_name=_('description'))
    plans = models.ManyToManyField(
        Plan,
        verbose_name=_('plans'),
        blank=True,
    )
    default = models.BooleanField(verbose_name=_('default'), default=False)
    is_active = models.BooleanField(verbose_name=_('is active'), default=True)
    last_sync_date = models.DateTimeField(null=True, blank=True, verbose_name=_('last sync date'))

    def __str__(self):
        return self.description

    class Meta:
        verbose_name = _('coverage')
        verbose_name_plural = _('coverage')
        ordering = ['code']


class Premium(ModelBase):
    coverage = models.ForeignKey(Coverage, verbose_name=_('coverage'), on_delete=models.PROTECT)
    use = models.ForeignKey(Use, verbose_name=_('use'), on_delete=models.PROTECT)
    plan = models.ForeignKey(Plan, verbose_name=_('plan'), on_delete=models.PROTECT, null=True)
    insured_amount = models.DecimalField(max_digits=50, decimal_places=2, verbose_name=_('price'), default=0.0)
    cost = models.DecimalField(max_digits=50, decimal_places=2, verbose_name=_('cost'), default=0.0)
    last_sync_date = models.DateTimeField(null=True, blank=True, verbose_name=_('last sync date'))

    class Meta:
        verbose_name = _('premium')
        verbose_name_plural = _('premiums')


class Mark(ModelBase):
    code = models.CharField(max_length=50, blank=True, verbose_name=_('code'))
    description = models.CharField(max_length=255, blank=True, verbose_name=_('description'))
    is_active = models.BooleanField(verbose_name=_('is active'), default=True)

    class Meta:
        verbose_name = _('mark')
        verbose_name_plural = _('marks')


class Model(ModelBase):
    mark = models.ForeignKey(Mark, verbose_name=_('mark'), on_delete=models.PROTECT)
    code = models.CharField(max_length=50, blank=True, verbose_name=_('code'))
    description = models.CharField(max_length=255, blank=True, verbose_name=_('description'))
    is_active = models.BooleanField(verbose_name=_('is active'), default=True)

    class Meta:
        verbose_name = _('model')
        verbose_name_plural = _('models')


def circulation_card_image_path(vehicle: 'Vehicle', file_name):
    return 'img/vehicle/circulation_card/{0}/{1}'.format(vehicle.license_plate, file_name)


def registration_certificate_image_path(vehicle: 'Vehicle', file_name):
    return 'img/vehicle/registration_certificate/{0}/{1}'.format(vehicle.license_plate, file_name)


def holder_s_license_image_path(vehicle: 'Vehicle', file_name):
    return 'img/vehicle/holder_s_license/{0}/{1}'.format(vehicle.license_plate, file_name)


def medical_certificate_image_path(vehicle: 'Vehicle', file_name):
    return 'img/vehicle/medical_certificate/{0}/{1}'.format(vehicle.license_plate, file_name)


def owner_rif_image_path(vehicle: 'Vehicle', file_name):
    return 'img/vehicle/owner/rif/{0}/{1}'.format(vehicle.license_plate, file_name)


def owner_medical_certificate_image_path(vehicle: 'Vehicle', file_name):
    return 'img/vehicle/owner/owner_medical_certificate/{0}/{1}'.format(vehicle.license_plate, file_name)


def owner_identity_card_image_path(vehicle: 'Vehicle', file_name):
    return 'img/vehicle/owner/identity_card/{0}/{1}'.format(vehicle.license_plate, file_name)


def owner_license_image_path(vehicle: 'Vehicle', file_name):
    return 'img/vehicle/owner/license/{0}/{1}'.format(vehicle.license_plate, file_name)


class Vehicle(ModelBase):
    SYNCHRONOUS = 1
    AUTOMATIC = 2

    TRANSMISSIONS = (
        (SYNCHRONOUS, _('Sincrónica')),
        (AUTOMATIC, _('Automática'))
    )
    model = models.ForeignKey(Model, verbose_name=_('model'), on_delete=models.PROTECT)
    serial_bodywork = models.CharField(max_length=50, blank=True, null=True, verbose_name=_('serial bodywork'))
    serial_engine = models.CharField(max_length=50, blank=True, null=True, verbose_name=_('serial engine'))
    license_plate = models.CharField(max_length=50, blank=True, null=True, verbose_name=_('license plate'))
    stalls = models.IntegerField(verbose_name='stalls', default=4)
    color = models.CharField(max_length=50, blank=True, null=True, verbose_name=_('color'))
    use = models.ForeignKey(Use, verbose_name=_('use'), on_delete=models.PROTECT)
    transmission = models.SmallIntegerField(choices=TRANSMISSIONS, default=SYNCHRONOUS, verbose_name=_('transmission'))
    owner_name = models.CharField(max_length=100, blank=True, null=True, verbose_name=_('owner name'),
                                  help_text="Nombre del dueño")
    owner_last_name = models.CharField(max_length=100, blank=True, null=True, verbose_name=_('owner lastname'),
                                       help_text="Apellido del dueño")
    owner_identity_card = models.ImageField(
        verbose_name=_('owner identity card'), upload_to=owner_identity_card_image_path, null=True,
        help_text="Cédula de identidad del dueño"
    )
    owner_rif = models.ImageField(verbose_name=_('owner_rif'), upload_to=owner_rif_image_path, null=True,
                                  help_text="RIF del dueño")
    owner_license = models.ImageField(
        verbose_name=_('owner license'), upload_to=owner_license_image_path, null=True,
        help_text="Licencia del dueño"
    )
    owner_medical_certificate = models.ImageField(
        verbose_name=_('owner medical certificate'), upload_to=owner_medical_certificate_image_path, null=True,
        help_text="Certificado médico del dueño"
    )
    taker = models.ForeignKey('security.User', verbose_name=_('taker'), on_delete=models.PROTECT)
    circulation_card = models.ImageField(verbose_name=_('circulation card'), upload_to=circulation_card_image_path,
                                         null=True, help_text="Carnet de circulación")
    registration_certificate = models.ImageField(
        verbose_name=_('registration certificate'), upload_to=registration_certificate_image_path, null=True,
        help_text="Certificado de registro de vehículo (Tiutlo)"
    )
    holder_s_license = models.ImageField(
        verbose_name=_('holder\'s license'), upload_to=holder_s_license_image_path, null=True,
        help_text="Licencia del tomador"
    )
    medical_certificate = models.ImageField(
        verbose_name=_('medical certificate'), upload_to=medical_certificate_image_path, null=True,
        help_text="Certificado médico"
    )

    class Meta:
        verbose_name = _('vehicle')
        verbose_name_plural = _('vehicles')
