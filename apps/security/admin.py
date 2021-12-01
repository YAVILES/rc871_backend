from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm
from django.utils.translation import ugettext_lazy as _
from import_export.resources import ModelResource
from import_export.admin import ImportExportModelAdmin

from apps.security.models import User, Role, Workflow


class UserResource(ModelResource):
    class Meta:
        model = User
        exclude = ('id', 'created', 'updated',)
        export_order = ('id', 'username', 'email', 'name')


class RoleResource(ModelResource):
    class Meta:
        model = Role
        exclude = ('id', 'created', 'updated',)


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
    list_display = ['username', 'email', 'name', 'last_name', 'is_staff', 'is_superuser', 'status']
    list_filter = ['username', 'email', 'status', 'is_staff', 'is_superuser']
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

