# Generated by Django 3.1.2 on 2022-06-02 11:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0042_policy_file'),
    ]

    operations = [
        migrations.AlterField(
            model_name='policy',
            name='number',
            field=models.PositiveIntegerField(db_index=True, default=None, null=True, verbose_name='number'),
        ),
    ]