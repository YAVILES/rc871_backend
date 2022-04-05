# Generated by Django 3.1.2 on 2022-04-05 19:53

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0028_auto_20220405_1537'),
    ]

    operations = [
        migrations.CreateModel(
            name='HistoricalChangeRate',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='created')),
                ('updated', models.DateTimeField(auto_now=True, verbose_name='updated')),
                ('valid_from', models.DateField(blank=True, verbose_name='valid_from')),
                ('valid_until', models.DateField(blank=True, verbose_name='valid_until')),
                ('rate', models.FloatField(default=0, verbose_name='rate')),
                ('last_sync_date', models.DateTimeField(blank=True, null=True, verbose_name='last sync date')),
            ],
            options={
                'verbose_name': 'historical change rate',
                'verbose_name_plural': 'historical change rates',
                'ordering': ['valid_from'],
            },
        ),
    ]
