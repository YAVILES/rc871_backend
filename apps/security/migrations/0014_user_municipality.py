# Generated by Django 3.1.2 on 2022-03-25 18:43

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0019_auto_20220324_1350'),
        ('security', '0013_auto_20220210_1253'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='municipality',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='core.municipality', verbose_name='municipality'),
        ),
    ]