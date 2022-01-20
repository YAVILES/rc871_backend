# Generated by Django 3.1.2 on 2022-01-19 19:28

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('core', '0010_premium_plan'),
    ]

    operations = [
        migrations.CreateModel(
            name='Mark',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='created')),
                ('updated', models.DateTimeField(auto_now=True, verbose_name='updated')),
                ('code', models.CharField(blank=True, max_length=50, verbose_name='code')),
                ('description', models.CharField(blank=True, max_length=255, verbose_name='description')),
            ],
            options={
                'verbose_name': 'mark',
                'verbose_name_plural': 'marks',
            },
        ),
        migrations.CreateModel(
            name='Model',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='created')),
                ('updated', models.DateTimeField(auto_now=True, verbose_name='updated')),
                ('code', models.CharField(blank=True, max_length=50, verbose_name='code')),
                ('description', models.CharField(blank=True, max_length=255, verbose_name='description')),
                ('mark', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='core.mark', verbose_name='mark')),
            ],
            options={
                'verbose_name': 'model',
                'verbose_name_plural': 'models',
            },
        ),
        migrations.CreateModel(
            name='Vehicle',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='created')),
                ('updated', models.DateTimeField(auto_now=True, verbose_name='updated')),
                ('serial_bodywork', models.CharField(blank=True, max_length=50, null=True, verbose_name='serial bodywork')),
                ('serial_engine', models.CharField(blank=True, max_length=50, null=True, verbose_name='serial engine')),
                ('license_plate', models.CharField(blank=True, max_length=50, null=True, verbose_name='license plate')),
                ('stalls', models.IntegerField(default=4, verbose_name='stalls')),
                ('color', models.CharField(blank=True, max_length=50, null=True, verbose_name='color')),
                ('transmission', models.SmallIntegerField(choices=[(1, 'Sincrónica'), (2, 'Automática')], default=1, verbose_name='transmission')),
                ('owner_data', models.JSONField(default=dict, verbose_name='owner data')),
                ('model', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='core.model', verbose_name='model')),
                ('taker', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL, verbose_name='taker')),
                ('use', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='core.use', verbose_name='use')),
            ],
            options={
                'verbose_name': 'vehicle',
                'verbose_name_plural': 'vehicles',
            },
        ),
    ]
