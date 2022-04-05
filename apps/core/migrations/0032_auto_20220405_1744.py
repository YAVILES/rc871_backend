# Generated by Django 3.1.2 on 2022-04-05 21:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0031_vehicle_owner_circulation_card'),
    ]

    operations = [
        migrations.AlterField(
            model_name='vehicle',
            name='serial_bodywork',
            field=models.CharField(blank=True, max_length=50, null=True, unique=True, verbose_name='serial bodywork'),
        ),
        migrations.AlterField(
            model_name='vehicle',
            name='serial_engine',
            field=models.CharField(blank=True, max_length=50, null=True, unique=True, verbose_name='serial engine'),
        ),
    ]
