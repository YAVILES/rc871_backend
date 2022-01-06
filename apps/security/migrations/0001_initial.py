# Generated by Django 3.1.2 on 2021-10-09 14:55

import django.contrib.gis.db.models.fields
from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='created')),
                ('updated', models.DateTimeField(auto_now=True, verbose_name='updated')),
                ('code', models.CharField(help_text='Código que se usaría para las sincronización con apps externas', max_length=255, null=True, unique=True, verbose_name='code')),
                ('username', models.CharField(max_length=50, null=True, unique=True, verbose_name='username')),
                ('email', models.EmailField(max_length=254, unique=True, verbose_name='email')),
                ('email_alternative', models.EmailField(max_length=254, null=True, verbose_name='email_alternative')),
                ('name', models.CharField(max_length=255, null=True, verbose_name='name')),
                ('last_name', models.CharField(max_length=50, verbose_name='last name')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('direction', models.CharField(max_length=255, null=True, verbose_name='direction')),
                ('phone', models.CharField(max_length=20, null=True, verbose_name='phone')),
                ('telephone', models.CharField(max_length=20, null=True, verbose_name='telephone')),
                ('point', django.contrib.gis.db.models.fields.PointField(null=True, srid=4326, verbose_name='point')),
                ('photo', models.ImageField(null=True, upload_to='photos/')),
                ('status', models.SmallIntegerField(choices=[(1, 'activo'), (0, 'inactivo'), (2, 'suspendo')], default=1, verbose_name='status')),
                ('is_staff', models.BooleanField(default=False, verbose_name='is staff')),
                ('is_superuser', models.BooleanField(default=False, verbose_name='is superuser')),
                ('is_active', models.BooleanField(default=True, verbose_name='is superuser')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('last_password_change', models.DateTimeField(auto_now_add=True, null=True, verbose_name='last password change')),
                ('jwt_id', models.UUIDField(blank=True, default=uuid.uuid4, null=True)),
                ('info', models.JSONField(default=dict)),
                ('last_sync_date', models.DateTimeField(blank=True, null=True, verbose_name='last sync date')),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
            },
        ),
    ]