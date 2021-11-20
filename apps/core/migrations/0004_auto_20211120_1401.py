# Generated by Django 3.1.2 on 2021-11-20 18:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_auto_20211120_1357'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='banner',
            options={'ordering': ['sequence_order'], 'verbose_name': 'banner', 'verbose_name_plural': 'banners'},
        ),
        migrations.RemoveField(
            model_name='banner',
            name='order',
        ),
        migrations.AddField(
            model_name='banner',
            name='sequence_order',
            field=models.IntegerField(default=1, verbose_name='sequence order'),
        ),
    ]
