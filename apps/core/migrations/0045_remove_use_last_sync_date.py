# Generated by Django 3.1.2 on 2022-06-11 02:56

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0044_remove_branchoffice_last_sync_date'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='use',
            name='last_sync_date',
        ),
    ]