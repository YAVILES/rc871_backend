# Generated by Django 3.1.2 on 2022-03-24 17:50

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0018_auto_20220322_1715'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='city',
            name='code',
        ),
        migrations.RemoveField(
            model_name='municipality',
            name='code',
        ),
        migrations.RemoveField(
            model_name='state',
            name='code',
        ),
    ]
