# Generated by Django 3.1.2 on 2022-04-08 16:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('security', '0020_auto_20220408_0057'),
    ]

    operations = [
        migrations.AddField(
            model_name='module',
            name='icon',
            field=models.CharField(max_length=255, null=True, verbose_name='icon'),
        ),
        migrations.AddField(
            model_name='workflow',
            name='icon',
            field=models.CharField(max_length=255, null=True, verbose_name='icon'),
        ),
    ]
