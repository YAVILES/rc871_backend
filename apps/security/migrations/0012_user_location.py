# Generated by Django 3.1.2 on 2022-02-10 16:45

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0015_location_link_google_maps'),
        ('security', '0011_user_identification_number'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='location',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='core.location', verbose_name='location'),
        ),
    ]
