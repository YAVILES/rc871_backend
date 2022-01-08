# Generated by Django 3.1.2 on 2022-01-08 01:54

import apps.core.models
from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_auto_20211120_1401'),
    ]

    operations = [
        migrations.CreateModel(
            name='BranchOffice',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='created')),
                ('updated', models.DateTimeField(auto_now=True, verbose_name='updated')),
                ('number', models.PositiveIntegerField(db_index=True, default=apps.core.models.get_branch_office_number, verbose_name='number')),
                ('code', models.CharField(blank=True, max_length=50, null=True, verbose_name='code')),
                ('description', models.CharField(max_length=100, verbose_name='description')),
                ('is_active', models.BooleanField(default=True, verbose_name='is active')),
                ('last_sync_date', models.DateTimeField(blank=True, null=True, verbose_name='last sync date')),
            ],
            options={
                'verbose_name': 'branch office',
                'verbose_name_plural': 'branch offices',
                'ordering': ['number'],
            },
        ),
    ]
