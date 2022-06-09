# Generated by Django 3.1.2 on 2022-06-02 18:56

from django.db import migrations
import multiselectfield.db.fields


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0007_auto_20220602_1255'),
    ]

    operations = [
        migrations.AddField(
            model_name='bank',
            name='coins',
            field=multiselectfield.db.fields.MultiSelectField(choices=[('USD', 'US Dollar'), ('VEF', 'Bolivar')], default=None, max_length=7, verbose_name='methods'),
        ),
    ]
