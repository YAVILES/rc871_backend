from django.contrib import admin

# Register your models here.
from import_export.fields import Field
from import_export.resources import ModelResource
from import_export.widgets import ForeignKeyWidget

from apps.core.models import Policy
from apps.payment.models import Bank, Payment
from apps.security.models import User


class PaymentResource(ModelResource):
    number = Field(attribute='number', column_name='Numero',  readonly=True)
    coin = Field(attribute='coin', column_name='Moneda', readonly=True)
    method = Field(attribute='get_method_display', column_name='Metodo', readonly=True)
    bank = Field(
        attribute='bank', widget=ForeignKeyWidget(Bank, 'description'), readonly=True, column_name='Banco'
    )
    policy = Field(
        attribute='policy', widget=ForeignKeyWidget(Policy, 'number'), readonly=True, column_name='Poliza'
    )
    user = Field(
        attribute='user', widget=ForeignKeyWidget(User, 'username'), readonly=True, column_name='Usuario'
    )
    reference = Field(attribute='reference', column_name='Referencia', readonly=True)
    comentary = Field(attribute='comentary', column_name='Comentario', readonly=True)
    change_factor = Field(attribute='change_factor_display', column_name='Factor de Cambio', readonly=True)
    status = Field(attribute='get_status_display', column_name='Estatus',  readonly=True)

    class Meta:
        model = Payment
        fields = ('number', 'reference', 'coin', 'method', 'bank', 'policy', 'comentary', 'user', 'change_factor',
                  'status',)
        import_id_fields = ('number',)


class BankResource(ModelResource):
    code = Field(attribute='code', column_name='Código')
    description = Field(attribute='description', column_name='Descripción')
    status = Field(attribute='get_status_display', column_name='Estatus',  readonly=True)

    class Meta:
        model = Bank
        fields = ('code', 'description', 'status',)
        import_id_fields = ('code',)

