# Generated by Django 3.1.2 on 2022-06-09 14:57

from django.db import migrations
import multiselectfield.db.fields


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0008_bank_coins'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bank',
            name='coins',
            field=multiselectfield.db.fields.MultiSelectField(choices=[('USD', 'US Dollar'), ('VEF', 'Bolivar')], default=None, max_length=7, verbose_name='coins'),
        ),
    ]