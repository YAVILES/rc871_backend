from django.conf import settings
from django.db import models

# Create your models here.
from django.db.models.signals import post_save
from money.currency import Currency, CurrencyHelper
from multiselectfield import MultiSelectField
from rest_framework import serializers
from sequences import get_next_value

from apps.core.models import ModelBase, Policy
from django.utils.translation import ugettext_lazy as _

from rc871_backend.settings import COINS
from rc871_backend.utils.functions import format_coin

TRANSFER = 0
MOBILE_PAYMENT = 1
CASH = 2
ZELLE = 3
OTHER = 4

METHODS = (
    (TRANSFER, _('Transferencia')),
    (MOBILE_PAYMENT, _('Pago móvil')),
    (CASH, _('Efectivo')),
    (ZELLE, _('Zelle')),
    (OTHER, _('Otro')),
)


def bank_archive_path(bank: 'Bank', file_name):
    return 'img/bank/{0}'.format(file_name)


class Bank(ModelBase):
    COINS_VALUES = [(coin.value, _(CurrencyHelper._CURRENCY_DATA[coin]['display_name'])) for coin in COINS]
    INACTIVE = 0
    ACTIVE = 1
    code = models.CharField(verbose_name=_('code'), max_length=255, blank=True, unique=True)
    description = models.CharField(verbose_name=_('description'), max_length=255)
    email = models.CharField(max_length=255, verbose_name=_('email'), null=True, blank=True)
    account_number = models.CharField(max_length=255, verbose_name=_('account_number'), null=True, blank=True)
    account_name = models.CharField(max_length=255, verbose_name=_('account_name'), null=True, blank=True)
    image = models.ImageField(verbose_name=_('image'), upload_to=bank_archive_path, null=True)
    methods = MultiSelectField(verbose_name=_('methods'), choices=METHODS, min_choices=1, default=None)
    coins = MultiSelectField(
        verbose_name=_('coins'), choices=COINS_VALUES, min_choices=1, default=None
    )
    status = models.SmallIntegerField(verbose_name=_('status'), default=ACTIVE, choices=(
        (ACTIVE, _('activo')),
        (INACTIVE, _('inactivo'))
    ))


def payment_archive_path(payment: 'Payment', file_name):
    return 'img/payment/{0}/{1}'.format(payment.number, file_name)


def payment_archive_igtf_path(payment: 'Payment', file_name):
    return 'img/payment/{0}/igtf/{1}'.format(payment.number, file_name)


def get_payment_number():
    return get_next_value('payment')


class Payment(ModelBase):
    PENDING = 0
    REJECTED = 1
    ACCEPTED = 2

    number = models.PositiveIntegerField(verbose_name='Number', primary_key=False, db_index=True,
                                         default=get_payment_number)
    amount = models.DecimalField(max_digits=50, decimal_places=2, default=0)
    commentary = models.CharField(null=True, blank=True, max_length=255, verbose_name=_('commentary'))
    method = models.SmallIntegerField(verbose_name=_('status'), default=TRANSFER, choices=METHODS)
    bank = models.ForeignKey(Bank, verbose_name=_('bank'), blank=True, null=True, on_delete=models.CASCADE)
    policy = models.ForeignKey(
        Policy, related_name='payments', verbose_name=_('order'), blank=True, null=True, on_delete=models.CASCADE
    )
    user = models.ForeignKey(
        'security.User', blank=True, null=True, related_name='user_payments', verbose_name=_('user'),
        on_delete=models.PROTECT
    )
    reference = models.CharField(verbose_name=_('reference'), max_length=255, null=False, blank=False)
    coin = models.CharField(max_length=255, verbose_name=_('coin'), default=settings.CURRENCY.value)
    archive = models.FileField(verbose_name=_('archive'), upload_to=payment_archive_path, null=True)
    change_factor = models.DecimalField(max_digits=50, decimal_places=2, verbose_name=_('change factor'), default=0.0)
    status = models.SmallIntegerField(verbose_name=_('status'), default=PENDING, choices=(
        (PENDING, _('pendiente')),
        (REJECTED, _('rechazado')),
        (ACCEPTED, _('aceptado'))
    ))

    @property
    def amount_display(self):
        return '{} {}'.format(format_coin(self.coin), str(self.amount))

    @property
    def change_factor_display(self):
        return '{} {}'.format(format_coin(Currency.VEF.value), str(self.change_factor))

    @property
    def total_full_bs_display(self):
        amount = self.total_full_bs
        return '{} {}'.format(format_coin(Currency.VEF.value), str(amount))


def post_save_payment(sender, instance: Payment, raw=False, **kwargs):
    if raw:
        return
    created = kwargs['created']
    try:
        if instance.policy:
            policy = instance.policy
            if instance.status == Payment.PENDING:
                policy.status = Policy.PENDING_APPROVAL
                policy.save(update_fields=['status'])
            elif instance.status == Payment.ACCEPTED and not policy.payments.filter(status=Payment.PENDING).exists():
                policy.status = Policy.PASSED
                policy.save(update_fields=['status'])

    except ValueError as e:
        raise serializers.ValidationError(detail={'error': _(e.__str__())})


post_save.connect(post_save_payment, sender=Payment)
