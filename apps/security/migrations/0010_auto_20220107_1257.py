# Generated by Django 3.1.2 on 2022-01-07 16:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('security', '0009_auto_20220107_1206'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='email',
            field=models.EmailField(max_length=254, verbose_name='email'),
        ),
    ]