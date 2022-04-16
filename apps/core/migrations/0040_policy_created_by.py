# Generated by Django 3.1.2 on 2022-04-16 01:53

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('core', '0039_auto_20220415_2040'),
    ]

    operations = [
        migrations.AddField(
            model_name='policy',
            name='created_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='policy_user', to=settings.AUTH_USER_MODEL, verbose_name='created by'),
        ),
    ]
