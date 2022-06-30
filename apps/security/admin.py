from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm
from django.utils.translation import gettext_lazy as _
from import_export.fields import Field
from import_export.resources import ModelResource
from import_export.admin import ImportExportModelAdmin
from import_export.widgets import ForeignKeyWidget, ManyToManyWidget

from apps.core.models import BranchOffice, Municipality
from apps.security.models import User, Role, Workflow


class UserResource(ModelResource):
    number = Field(attribute="number", column_name='Numero', readonly=True)
    username = Field(attribute="username", column_name='Login', readonly=True)
    email = Field(attribute="email", column_name='Correo', readonly=True)
    email_alternative = Field(attribute="email_alternative", column_name='Correo Alternativo', readonly=True)
    name = Field(attribute="name", column_name='Nombre', readonly=True)
    last_name = Field(attribute="last_name", column_name='Apellido', readonly=True)
    identification_number = Field(attribute="identification_number", column_name='Cédula de Identidad', readonly=True)
    direction = Field(attribute="direction", column_name='Dirección', readonly=True)
    phone = Field(attribute="phone", column_name='Numero Celular', readonly=True)
    telephone = Field(attribute="telephone", column_name='Numero Telefono', readonly=True)
    branch_office = Field(
        attribute='branch_office', widget=ForeignKeyWidget(BranchOffice, 'description'), column_name='Sucursal',
        readonly=True
    )
    state = Field(
        attribute='city', widget=ForeignKeyWidget(Municipality, 'city__state__description'), column_name='Estado',
        readonly=True
    )
    city = Field(
        attribute='city', widget=ForeignKeyWidget(Municipality, 'city__description'), column_name='Ciudad',
        readonly=True
    )
    municipality = Field(
        attribute='municipality', widget=ForeignKeyWidget(Municipality, 'description'), column_name='Municipio',
        readonly=True
    )
    roles = Field(
        attribute='roles', widget=ManyToManyWidget(Role, ',', 'name'), column_name='Roles'
    )
    created = Field(attribute="created", column_name='Fecha de creación', readonly=True)
    is_adviser = Field(attribute="is_adviser", column_name='Es Asesor', readonly=True)
    is_staff = Field(attribute="is_staff", column_name='Es Empleado', readonly=True)
    is_active = Field(attribute='is_active', column_name='Activo')

    class Meta:
        model = User
        exclude = ('id', 'created', 'updated', 'point', 'holder_s_license', 'medical_certificate', 'circulation_card',
                   'photo', 'password', 'code', 'is_superuser', 'is_staff', 'last_login', 'jwt_id', 'info',
                   'last_password_change', 'last_sync_date', 'user_work_flows', 'user_permissions', 'groups',)


class RoleResource(ModelResource):
    name = Field(attribute='name', column_name='Nombre')
    is_active = Field(attribute='is_active', column_name='Activo')

    class Meta:
        model = Role
        exclude = ('id', 'created', 'updated', 'workflows',)
        import_id_fields = ('name',)


@admin.register(Workflow)
class BrandAdmin(admin.ModelAdmin):
    list_display = ('title', 'url',)


class CustomUserChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = User


class UserResourceAdmin(ImportExportModelAdmin):
    resource_class = UserResource


class CustomUserAdmin(UserAdmin, ImportExportModelAdmin):
    form = CustomUserChangeForm
    list_display = ['username', 'email', 'name', 'last_name', 'is_staff', 'is_superuser', 'is_active']
    list_filter = ['username', 'email', 'is_active', 'is_staff', 'is_superuser']
    filter_horizontal = ['roles']
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'), {'fields': ('name', 'last_name')}),
        (_('Workflows'), {
            'fields': ('is_staff', 'is_superuser', 'roles', 'user_work_flows'),
        }),
        (_('Important dates'), {'fields': ('last_login',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2'),
        }),
    )
    search_fields = ('username', 'email', 'code',)
    ordering = ('email',)


admin.site.register(User, CustomUserAdmin)

