import uuid

from constance.backends.database.models import Constance
from django.conf import settings

from auditlog.registry import auditlog
from django.contrib.gis.db import models as geo_models
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin, Group, Permission
from django.db import models
from django.db.models.signals import post_save
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _

# Create your models here.
from apps.client.models import Client
from apps.core.models import ModelBase, Product, Menu
from apps.inventory.models import Warehouse


class RecoveryQuestions(ModelBase):
    INACTIVE = 0
    ACTIVE = 1
    question = models.CharField(max_length=255, verbose_name=_('question'), unique=True)
    status = models.SmallIntegerField(choices=(
        (ACTIVE, _('activo')),
        (INACTIVE, _('inactivo'))
    ), default=ACTIVE, verbose_name=_('status'))


class UserRecoveryQuestions(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey('security.User', verbose_name=_(
        'user'), on_delete=models.CASCADE)
    question = models.ForeignKey(RecoveryQuestions, verbose_name=_(
        'question'), on_delete=models.PROTECT)
    answer = models.CharField(max_length=255, verbose_name=_('answer'))


class WarehouseUser(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    warehouse = models.ForeignKey(Warehouse, verbose_name=_(
        'warehouse'), on_delete=models.PROTECT)
    user = models.ForeignKey('security.User', verbose_name=_(
        'user'), on_delete=models.PROTECT)
    last_sync_date = models.DateTimeField(null=True, blank=True, verbose_name=_('last sync date'))


class ClientUser(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    client = models.ForeignKey(Client, verbose_name=_('client'), on_delete=models.PROTECT)
    user = models.ForeignKey('security.User', verbose_name=_('user'), on_delete=models.PROTECT)
    last_sync_date = models.DateTimeField(null=True, blank=True, verbose_name=_('last sync date'))


class UserManager(BaseUserManager):
    def system(self):
        user, _ = self.get_or_create(
            email='system@example.com',
            name='SYSTEM',
            last_name='SYSTEM',
            # Como es plain text deberia ser suficiente para que el usuario no haga login
            password='SYSTEM',
            status=User.INACTIVE
        )
        return user

    def admin(self, database='default'):
        user, created = User.objects.using(database).get_or_create(
            email='admin@admin.com',
            name='Admin',
            last_name='User',
            # Como es plain text deberia ser suficiente para que el usuario no haga login
            status=User.ACTIVE
        )

        group, _ = Group.objects.using(database).get_or_create(name="Admin")
        group.permissions.set(
            Menu.objects.filter(permissions__isnull=False).values_list('permissions__id', flat=True)
        )
        user.groups.set([group])
        user.set_password('admin1234567')
        user.save(using=database)
        return user

    def web(self):
        user, _ = self.get_or_create(
            email='web@example.com',
            name='WEB',
            last_name='WEB',
            # Como es plain text deberia ser suficiente para que el usuario no haga login
            password='WEB',
            status=User.INACTIVE
        )
        return user

    def _create_user(self, email, name, last_name, password, database='default', **extra_fields):
        """
        Creates and saves a User with the given username, email and password.
        """
        if not email:
            raise ValueError(_('The Email must be set'))
        email = self.normalize_email(email)
        obj = User(email=email, name=name, last_name=last_name, **extra_fields)
        obj.set_password(password)
        obj.save(using=database)
        return obj

    def create_user(self, email, name=None, last_name=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, name, last_name, password, **extra_fields)

    def create_superuser(self, email, name, last_name, password, database='default', **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_verified', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, name, last_name, password, database, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin, ModelBase):
    INACTIVE = 0
    ACTIVE = 1
    SUSPEND = 2
    STATUS = (
        (ACTIVE, _('activo')),
        (INACTIVE, _('inactivo')),
        (SUSPEND, _('suspendo')),
    )

    code = models.CharField(max_length=255, verbose_name=_('code'), null=True, unique=True,
                            help_text="Código que se usaría para las sincronización con apps externas")
    username = models.CharField(max_length=50, verbose_name=_('username'), null=True, unique=True)
    email = models.EmailField(verbose_name=_('email'), unique=True)
    email_alternative = models.EmailField(null=True, verbose_name=_('email_alternative'))
    name = models.CharField(max_length=255, verbose_name=_('name'), null=True)
    last_name = models.CharField(max_length=50, verbose_name=_('last name'))
    password = models.CharField(max_length=128, verbose_name=_('password'))
    direction = models.CharField(null=True, max_length=255, verbose_name=_('direction'))
    phone = models.CharField(null=True, max_length=20, verbose_name=_('phone'))
    telephone = models.CharField(null=True, max_length=20, verbose_name=_('telephone'))
    point = geo_models.PointField(verbose_name=_('point'), null=True)
    photo = models.ImageField(upload_to='photos/', null=True)
    status = models.SmallIntegerField(choices=STATUS, default=ACTIVE, verbose_name=_('status'))
    is_staff = models.BooleanField(verbose_name=_('is staff'), default=False)
    is_superuser = models.BooleanField(verbose_name=_('is superuser'), default=False)
    is_active = models.BooleanField(verbose_name=_('is superuser'), default=True)
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email', 'name', 'last_name', 'phone']
    last_login = models.DateTimeField(blank=True, null=True, verbose_name=_('last login'))
    last_password_change = models.DateTimeField(blank=True, null=True, auto_now_add=True, verbose_name=_('last password change'))
    jwt_id = models.UUIDField(default=uuid.uuid4, blank=True, null=True)
    info = models.JSONField(default=dict)
    last_sync_date = models.DateTimeField(null=True, blank=True, verbose_name=_('last sync date'))
    objects = UserManager()

    @property
    def last_ip_address(self):
        try:
            return self.info['ip']
        except (ValueError, KeyError):
            return None

    def get_short_name(self):
        return self.name

    def __str__(self):
        return "{full_name}".format(full_name=self.get_full_name())

    def get_full_name(self):
        return "{name} {last_name}".format(name=self.name, last_name=self.last_name)

    @cached_property
    def full_name(self):
        return self.get_full_name()

    """
        Deletes an user
    """
    def delete(self, using=None, keep_parents=False):
        models.signals.pre_delete.send(sender=self.__class__,
                                       instance=self,
                                       using=using)

        self.status = User.INACTIVE
        self.save(update_fields=['status', ])
        models.signals.post_delete.send(sender=self.__class__,
                                        instance=self,
                                        using=using)

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')


"""
    AuditLog
"""
auditlog.register(User, exclude_fields=['created', 'updated'])
auditlog.register(Group, exclude_fields=['created', 'updated'])
auditlog.register(Permission, exclude_fields=['created', 'updated'])