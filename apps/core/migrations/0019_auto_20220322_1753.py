# Generated by Django 3.1.2 on 2022-03-22 21:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0018_auto_20220322_1715'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='state',
            name='created',
        ),
        migrations.RemoveField(
            model_name='state',
            name='updated',
        ),
        migrations.AlterField(
            model_name='state',
            name='id',
            field=models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
    ]
