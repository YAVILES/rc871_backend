# Generated by Django 4.0.5 on 2022-09-27 14:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0007_alter_banner_content_alter_banner_subtitle_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='section',
            name='content',
            field=models.CharField(default='', max_length=300, verbose_name='content'),
        ),
        migrations.AlterField(
            model_name='section',
            name='subtitle',
            field=models.CharField(default='', max_length=100, verbose_name='subtitle'),
        ),
        migrations.AlterField(
            model_name='section',
            name='url',
            field=models.CharField(default='', max_length=255, verbose_name='url'),
        ),
    ]
