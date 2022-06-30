import uuid

from django.contrib.gis.db import models as geo_models
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.db import models
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import PermissionsMixin
from sequences import get_next_value

from apps.core.models import ModelBase, BranchOffice, Municipality


class Module(ModelBase):
    title = models.CharField(max_length=100, verbose_name=_('title'))
    icon = models.CharField(max_length=255, verbose_name=_('icon'), null=True)

    class Meta:
        verbose_name = _('module')
        verbose_name_plural = _('modules')


class Workflow(ModelBase):
    module = models.ForeignKey(Module, verbose_name=_('module'), null=True, on_delete=models.CASCADE)
    title = models.CharField(max_length=100, verbose_name=_('title'))
    url = models.CharField(max_length=255, verbose_name=_('url'))
    icon = models.CharField(max_length=255, verbose_name=_('icon'), null=True)

    class Meta:
        verbose_name = _('workflow')
        verbose_name_plural = _('work flows')


class Role(models.Model):
    name = models.CharField(_('name'), max_length=150, unique=True)
    workflows = models.ManyToManyField(
        Workflow,
        verbose_name=_('work flows'),
        blank=True,
    )
    is_active = models.BooleanField(verbose_name=_('is active'), default=True)

    class Meta:
        verbose_name = _('role')
        verbose_name_plural = _('roles')

    def __str__(self):
        return self.name


def medical_certificate_image_path(user: 'security.User', file_name):
    return 'img/user/medical_certificate/{0}/{1}'.format(user.username, file_name)


def holder_s_license_image_path(user: 'security.User', file_name):
    return 'img/user/holder_s_license/{0}/{1}'.format(user.username, file_name)


def circulation_card_image_path(user: 'security.User', file_name):
    return 'img/user/circulation_card/{0}/{1}'.format(user.username, file_name)


class UserManager(BaseUserManager):
    def system(self):
        user, _ = self.get_or_create(
            username='system',
            email='system@example.com',
            name='SYSTEM',
            last_name='SYSTEM',
            # Como es plain text deberia ser suficiente para que el usuario no haga login
            password='SYSTEM',
            is_active=False
        )
        return user

    def web(self):
        user, _ = self.get_or_create(
            username='web',
            email='web@example.com',
            name='WEB',
            last_name='WEB',
            # Como es plain text deberia ser suficiente para que el usuario no haga login
            password='web',
            is_active=False
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

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, name, last_name, password, database, **extra_fields)


def get_user_number():
    return get_next_value('user_number')


class User(AbstractBaseUser, PermissionsMixin, ModelBase):
    code = models.CharField(max_length=255, verbose_name=_('code'), null=True, unique=True,
                            help_text="Código que se usaría para las sincronización con apps externas")
    number = models.PositiveIntegerField(verbose_name='Number', primary_key=False, db_index=True, null=True,
                                         default=get_user_number)
    username = models.CharField(max_length=50, verbose_name=_('username'), null=True, unique=True)
    email = models.EmailField(verbose_name=_('email'))
    email_alternative = models.EmailField(null=True, verbose_name=_('email_alternative'))
    identification_number = models.CharField(
        max_length=50, unique=True, verbose_name=_('identification_number'), null=True
    )
    name = models.CharField(max_length=255, verbose_name=_('name'), null=True)
    last_name = models.CharField(max_length=50, verbose_name=_('last name'))
    password = models.CharField(max_length=128, verbose_name=_('password'))
    direction = models.CharField(null=True, max_length=255, verbose_name=_('direction'))
    phone = models.CharField(null=True, max_length=20, verbose_name=_('phone'))
    telephone = models.CharField(null=True, blank=True, max_length=20, verbose_name=_('telephone'))
    point = geo_models.PointField(verbose_name=_('point'), null=True)
    photo = models.ImageField(upload_to='photos/', null=True)
    holder_s_license = models.ImageField(
        verbose_name=_('holder\'s license'), upload_to=holder_s_license_image_path, null=True,
        help_text="Licencia del tomador"
    )
    medical_certificate = models.ImageField(
        verbose_name=_('medical certificate'), upload_to=medical_certificate_image_path, null=True,
        help_text="Certificado médico"
    )
    circulation_card = models.ImageField(verbose_name=_('circulation card'), upload_to=circulation_card_image_path,
                                         null=True, help_text="Carnet de circulación")
    is_adviser = models.BooleanField(
        _('is adviser'),
        default=False,
        help_text=_(
            'Define si el usuario es un asesor.'
        ),
    )
    is_superuser = models.BooleanField(
        _('is superuser'),
        default=False,
        help_text=_(
            'Designates that this user has all permissions without '
            'explicitly assigning them.'
        ),
    )
    roles = models.ManyToManyField(
        Role,
        verbose_name=_('roles'),
        blank=True,
        help_text=_(
            'The roles this user belongs to. A user will get all workflows '
            'granted to each of their roles.'
        ),
        related_name="user_set",
        related_query_name="user",
    )
    user_work_flows = models.ManyToManyField(
        Workflow,
        verbose_name=_('user work flows'),
        blank=True,
        help_text=_('Specific work flows for this user.'),
        related_name="user_set",
        related_query_name="user",
    )
    is_staff = models.BooleanField(verbose_name=_('is staff'), default=False)
    branch_office = models.ForeignKey(BranchOffice, blank=True, null=True, verbose_name=_('branch_office'),
                                      on_delete=models.PROTECT)
    municipality = models.ForeignKey(Municipality, blank=True, null=True, verbose_name=_('municipality'),
                                     on_delete=models.PROTECT)
    is_active = models.BooleanField(verbose_name=_('is active'), default=True)
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email', 'name', 'last_name', 'phone']
    last_login = models.DateTimeField(blank=True, null=True, verbose_name=_('last login'))
    last_password_change = models.DateTimeField(blank=True, null=True, auto_now_add=True,
                                                verbose_name=_('last password change'))
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

        self.is_active = False
        self.save(update_fields=['is_active', ])
        models.signals.post_delete.send(sender=self.__class__,
                                        instance=self,
                                        using=using)

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
