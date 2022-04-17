import uuid
from datetime import datetime
from decimal import Decimal
from os import remove
from os import path
from constance import config
from constance.backends.database.models import Constance
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.db.models.signals import post_save
from sequences import get_next_value
from django.contrib.gis.db import models as geo_models
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

    class Meta:
        verbose_name = _('location')
        verbose_name_plural = _('locations')
        verbose_name_plural = _('locations')
        ordering = ['description']


def banner_image_path(banner: 'Banner', file_name):
    return 'img/banner/{0}'.format(file_name)


class Banner(ModelBase):
    title = models.CharField(max_length=100, verbose_name=_('title'))
    subtitle = models.CharField(max_length=100, verbose_name=_('subtitle'))
    content = models.CharField(max_length=255, verbose_name=_('content'))
    image = models.ImageField(upload_to=banner_image_path, null=True, verbose_name=_('image'))
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
    link_google_maps = models.CharField(null=True, blank=True, max_length=350, verbose_name=_('link google maps'))
    geo_location = geo_models.PointField(verbose_name=_('geo location'), null=True)
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
        query = self.coverage_set.filter(default=False, is_active=True)
        query_default = Coverage.objects.filter(default=True, is_active=True)
        return query_default.union(query).order_by('default', 'created', )

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

    @property
    def insured_amount_display(self):
        return '{} {}'.format(settings.CURRENCY_FORMAT, self.insured_amount)

    @property
    def cost_display(self):
        return '{} {}'.format(settings.CURRENCY_FORMAT, self.cost)

    @property
    def insured_amount_change(self):
        try:
            change_factor = Constance.objects.get(key="CHANGE_FACTOR").value
        except ObjectDoesNotExist:
            getattr(config, "CHANGE_FACTOR")
            change_factor = Constance.objects.get(key="CHANGE_FACTOR").value
        return float(format(self.insured_amount * Decimal(change_factor), ".2f"))

    @property
    def insured_amount_change_display(self):
        return '{} {}'.format(settings.CURRENCY_CHANGE_FORMAT, self.insured_amount_change)

    @property
    def cost_change(self):
        try:
            change_factor = Constance.objects.get(key="CHANGE_FACTOR").value
        except ObjectDoesNotExist:
            getattr(config, "CHANGE_FACTOR")
            change_factor = Constance.objects.get(key="CHANGE_FACTOR").value

        return float(format(self.cost * Decimal(change_factor), ".2f"))

    @property
    def cost_change_display(self):
        return '{} {}'.format(settings.CURRENCY_CHANGE_FORMAT, self.cost_change)

    class Meta:
        verbose_name = _('premium')
        verbose_name_plural = _('premiums')


class Mark(ModelBase):
    description = models.CharField(max_length=255, blank=True, unique=True, db_index=True,
                                   verbose_name=_('description'))
    is_active = models.BooleanField(verbose_name=_('is active'), default=True)

    class Meta:
        verbose_name = _('mark')
        verbose_name_plural = _('marks')


class Model(ModelBase):
    mark = models.ForeignKey(Mark, verbose_name=_('mark'), on_delete=models.PROTECT)
    description = models.CharField(max_length=255, blank=True, verbose_name=_('description'))
    is_active = models.BooleanField(verbose_name=_('is active'), default=True)

    class Meta:
        verbose_name = _('model')
        verbose_name_plural = _('models')


def medical_certificate_image_path(user: 'security.User', file_name):
    return 'img/user/medical_certificate/{0}/{1}'.format(user.username, file_name)


def holder_s_license_image_path(user: 'security.User', file_name):
    return 'img/user/holder_s_license/{0}/{1}'.format(user.username, file_name)


def circulation_card_image_path(user: 'security.User', file_name):
    return 'img/user/circulation_card/{0}/{1}'.format(user.username, file_name)


def owner_circulation_card_image_path(vehicle: 'Vehicle', file_name):
    return 'img/vehicle/circulation_card/{0}/{1}'.format(vehicle.license_plate, file_name)


def registration_certificate_image_path(vehicle: 'Vehicle', file_name):
    return 'img/vehicle/registration_certificate/{0}/{1}'.format(vehicle.license_plate, file_name)


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
    year = models.CharField(max_length=5, null=True, blank=True)
    use = models.ForeignKey(Use, verbose_name=_('use'), on_delete=models.PROTECT)
    transmission = models.SmallIntegerField(choices=TRANSMISSIONS, default=SYNCHRONOUS, verbose_name=_('transmission'))
    owner_name = models.CharField(max_length=100, blank=True, null=True, verbose_name=_('owner name'),
                                  help_text="Nombre del dueño")
    owner_last_name = models.CharField(max_length=100, blank=True, null=True, verbose_name=_('owner lastname'),
                                       help_text="Apellido del dueño")
    owner_identity_card = models.CharField(max_length=100, blank=True, null=True, verbose_name=_('owner_identity_card'),
                                           help_text="Cedula del dueño")
    owner_identity_card_image = models.ImageField(
        verbose_name=_('owner identity card'), upload_to=owner_identity_card_image_path, null=True,
        help_text="Cédula de identidad del dueño Imagen"
    )
    owner_license = models.ImageField(
        verbose_name=_('owner license'), upload_to=owner_license_image_path, null=True,
        help_text="Licencia del dueño"
    )
    owner_medical_certificate = models.ImageField(
        verbose_name=_('owner medical certificate'), upload_to=owner_medical_certificate_image_path, null=True,
        help_text="Certificado médico del dueño"
    )
    owner_circulation_card = models.ImageField(
        verbose_name=_('owner circulation card'), upload_to=owner_circulation_card_image_path, null=True,
        help_text="Carnet de circulación del dueño"
    )
    owner_phones = models.CharField(max_length=100, blank=True, null=True, verbose_name=_('owner phones'),
                                    help_text="Telefonos del dueño")
    owner_address = models.CharField(max_length=100, blank=True, null=True, verbose_name=_('owner address'),
                                     help_text="Dirección del dueño")
    owner_email = models.EmailField(max_length=100, blank=True, null=True, verbose_name=_('owner email'),
                                    help_text="Correo del dueño")
    taker = models.ForeignKey('security.User', verbose_name=_('taker'), on_delete=models.PROTECT, null=True)
    is_active = models.BooleanField(verbose_name=_('is active'), default=True)

    class Meta:
        verbose_name = _('vehicle')
        verbose_name_plural = _('vehicles')


def get_state_number():
    return get_next_value('state_number')


class State(ModelBase):
    number = models.PositiveIntegerField(verbose_name='number', primary_key=False, db_index=True,
                                         default=get_state_number)
    description = models.CharField(max_length=100, verbose_name=_('description'))

    class Meta:
        verbose_name = _('state')
        verbose_name_plural = _('state')


def get_city_number():
    return get_next_value('city_number')


class City(ModelBase):
    number = models.PositiveIntegerField(verbose_name='number', primary_key=False, db_index=True,
                                         default=get_city_number)
    description = models.CharField(max_length=100, verbose_name=_('description'))
    state = models.ForeignKey(State, verbose_name=_('state'), on_delete=models.PROTECT)

    class Meta:
        verbose_name = _('city')
        verbose_name_plural = _('cities')


def get_municipality_number():
    return get_next_value('municipality_number')


class Municipality(ModelBase):
    number = models.PositiveIntegerField(verbose_name='number', primary_key=False, db_index=True,
                                         default=get_municipality_number)
    description = models.CharField(max_length=100, verbose_name=_('description'))
    city = models.ForeignKey(City, verbose_name=_('city'), on_delete=models.PROTECT)

    class Meta:
        verbose_name = _('municipality')
        verbose_name_plural = _('municipalities')


def get_policy_number():
    return get_next_value('get_policy_number')


def qrcode_image_path(policy: 'Policy', file_name):
    return 'file/policy/{0}/{1}'.format(policy.number, file_name)


def file_policy_path(policy: 'Policy', file_name):
    return 'file/policy/{0}/{1}'.format(policy.number, file_name)


class Policy(ModelBase):
    OUTSTANDING = 0
    PENDING_APPROVAL = 1  # pendiente de pago
    PASSED = 2  # aprobado
    EXPIRED = 3
    REJECTED = 4

    STATUSES = (
        (OUTSTANDING, _('pendiente de pago')),
        (PENDING_APPROVAL, _('pendiente de aprobación')),
        (PASSED, _('aprobado')),
        (EXPIRED, _('vencido')),
        (REJECTED, _('rechazado')),
    )

    RCV = 0
    TYPES = (
        (RCV, _('RCV')),
    )

    NEW = 0
    ACTIONS = (
        (NEW, _('Nueva')),
    )

    number = models.PositiveIntegerField(verbose_name='number', primary_key=False, db_index=True,
                                         default=get_policy_number)
    taker = models.ForeignKey('security.User', verbose_name=_('taker'), on_delete=models.PROTECT)
    adviser = models.ForeignKey('security.User', related_name="policy_adviser", verbose_name=_('adviser'),
                                on_delete=models.PROTECT)
    created_by = models.ForeignKey('security.User', related_name="policy_user", verbose_name=_('created by'),
                                   on_delete=models.PROTECT, null=True)
    vehicle = models.ForeignKey(Vehicle, verbose_name=_('vehicle'), on_delete=models.PROTECT)
    type = models.SmallIntegerField(choices=TYPES, default=RCV, verbose_name=_('type'))
    action = models.SmallIntegerField(choices=ACTIONS, default=NEW, verbose_name=_('action'))
    due_date = models.DateTimeField(verbose_name=_('due_date'), null=True, help_text="Fecha de vencimiento")
    plan = models.ForeignKey(Plan, verbose_name=_('plan'), null=True, on_delete=models.PROTECT)
    status = models.SmallIntegerField(choices=STATUSES, default=OUTSTANDING, verbose_name=_('status'))
    total_amount = models.DecimalField(max_digits=50, decimal_places=2, verbose_name=_('total'), default=0.0)
    total_insured_amount = models.DecimalField(max_digits=50, decimal_places=2, verbose_name=_('total'), default=0.0)
    change_factor = models.DecimalField(max_digits=50, decimal_places=2, verbose_name=_('change factor'), default=0.0)
    qrcode = models.ImageField(upload_to=qrcode_image_path, null=True, verbose_name=_('qrcode image'))
    file = models.FileField(upload_to=file_policy_path, null=True, verbose_name=_('file policy pdf'))

    @property
    def total_amount_display(self):
        return '{} {}'.format(settings.CURRENCY_FORMAT, self.total_amount)

    @property
    def total_amount_change(self):
        return float(format(Decimal(self.total_amount) * Decimal(self.change_factor), ".2f"))

    @property
    def total_amount_change_display(self):
        return '{} {}'.format(settings.CURRENCY_CHANGE_FORMAT, self.total_amount_change)

    @property
    def total_insured_amount_display(self):
        return '{} {}'.format(settings.CURRENCY_FORMAT, self.total_insured_amount)

    @property
    def total_insured_amount_change(self):
        return float(format(Decimal(self.total_insured_amount) * Decimal(self.change_factor), ".2f"))

    @property
    def total_insured_amount_change_display(self):
        return '{} {}'.format(settings.CURRENCY_CHANGE_FORMAT, self.total_insured_amount_change)

    class Meta:
        verbose_name = _('policy')
        verbose_name_plural = _('policies')
        ordering = ['-number']


def get_policy_coverage_number():
    return get_next_value('get_policy_coverage_number')


class PolicyCoverage(ModelBase):
    number = models.PositiveIntegerField(verbose_name='number', primary_key=False, db_index=True,
                                         default=get_policy_coverage_number)
    policy = models.ForeignKey(Policy, related_name='items', verbose_name=_('policy'), blank=True, null=True,
                               on_delete=models.PROTECT)
    coverage = models.ForeignKey(Coverage, verbose_name=_('coverage'), blank=True, null=True, on_delete=models.PROTECT)
    insured_amount = models.DecimalField(max_digits=50, decimal_places=2, verbose_name=_('price'), default=0.0)
    cost = models.DecimalField(max_digits=50, decimal_places=2, verbose_name=_('cost'), default=0.0)

    @property
    def insured_amount_display(self):
        return '{} {}'.format(settings.CURRENCY_FORMAT, self.insured_amount)

    @property
    def insured_amount_change(self):
        return float(format(self.insured_amount * Decimal(self.policy.change_factor), ".2f"))

    @property
    def insured_amount_change_display(self):
        return '{} {}'.format(settings.CURRENCY_CHANGE_FORMAT, self.insured_amount_change)

    @property
    def cost_display(self):
        return '{} {}'.format(settings.CURRENCY_FORMAT, self.cost)

    @property
    def cost_change(self):
        return float(format(self.insured_amount * Decimal(self.policy.change_factor), ".2f"))

    @property
    def cost_change_display(self):
        return '{} {}'.format(settings.CURRENCY_CHANGE_FORMAT, self.insured_amount_change)

    class Meta:
        verbose_name = _('item')
        verbose_name_plural = _('items')
        ordering = ['number']


class HistoricalChangeRate(ModelBase):
    valid_from = models.DateField(verbose_name="valid_from", null=False, blank=True)
    valid_until = models.DateField(verbose_name="valid_until", null=False, blank=True)
    rate = models.FloatField(verbose_name="rate", default=0)
    last_sync_date = models.DateTimeField(null=True, blank=True, verbose_name=_('last sync date'))

    class Meta:
        verbose_name = _('historical change rate')
        verbose_name_plural = _('historical change rates')
        ordering = ['valid_from']


def update_change_rate(sender, instance: HistoricalChangeRate, **kwargs):
    using = kwargs['using']
    created = kwargs['created']
    today = datetime.today().date()
    if instance.valid_from <= today <= instance.valid_until:
        try:
            change_factor = Constance.objects.get(key="CHANGE_FACTOR")
            change_factor.value = float(instance.rate)
            change_factor.save(update_fields=['value'])
        except ObjectDoesNotExist:
            Constance.objects.create(
                key="CHANGE_FACTOR",
                value=float(instance.rate)
            )


post_save.connect(update_change_rate, sender=HistoricalChangeRate)
