# Generated by Django 3.1.2 on 2022-04-01 20:45

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0023_auto_20220401_1640'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='vehicle',
            name='owner_rif',
        ),
        migrations.RemoveField(
            model_name='vehicle',
            name='owner_rif_image',
        ),
    ]