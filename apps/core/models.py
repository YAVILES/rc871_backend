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
