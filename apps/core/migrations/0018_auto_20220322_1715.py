# Generated by Django 3.1.2 on 2022-03-22 21:15

import apps.core.models
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0017_vehicle_is_active'),
    ]

    operations = [
        migrations.CreateModel(
            name='City',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='created')),
                ('updated', models.DateTimeField(auto_now=True, verbose_name='updated')),
                ('number', models.PositiveIntegerField(db_index=True, default=apps.core.models.get_city_number, verbose_name='number')),
                ('code', models.CharField(blank=True, max_length=50, null=True, verbose_name='code')),
                ('description', models.CharField(max_length=100, verbose_name='description')),
            ],
            options={
                'verbose_name': 'city',
                'verbose_name_plural': 'cities',
            },
        ),
        migrations.CreateModel(
            name='State',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='created')),
                ('updated', models.DateTimeField(auto_now=True, verbose_name='updated')),
                ('number', models.PositiveIntegerField(db_index=True, default=apps.core.models.get_state_number, verbose_name='number')),
                ('code', models.CharField(blank=True, max_length=50, null=True, verbose_name='code')),
                ('description', models.CharField(max_length=100, verbose_name='description')),
            ],
            options={
                'verbose_name': 'state',
                'verbose_name_plural': 'state',
            },
        ),
        migrations.CreateModel(
            name='Municipality',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='created')),
                ('updated', models.DateTimeField(auto_now=True, verbose_name='updated')),
                ('number', models.PositiveIntegerField(db_index=True, default=apps.core.models.get_municipality_number, verbose_name='number')),
                ('code', models.CharField(blank=True, max_length=50, null=True, verbose_name='code')),
                ('description', models.CharField(max_length=100, verbose_name='description')),
                ('city', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='core.city', verbose_name='city')),
            ],
            options={
                'verbose_name': 'municipality',
                'verbose_name_plural': 'municipalities',
            },
        ),
        migrations.AddField(
            model_name='city',
            name='state',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='core.state', verbose_name='state'),
        ),
    ]
