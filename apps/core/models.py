import uuid
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
