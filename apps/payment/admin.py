from django.contrib import admin

# Register your models here.
from import_export.fields import Field
from import_export.resources import ModelResource

from apps.payment.models import Bank


class BankResource(ModelResource):
    code = Field(attribute='code', column_name='Código')
    description = Field(attribute='description', column_name='Descripción')
    status = Field(attribute='status', column_name='Estatus')

    class Meta:
        model = Bank
        fields = ('code', 'description', 'status',)
        import_id_fields = ('code',)

