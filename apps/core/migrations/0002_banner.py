# Generated by Django 3.1.2 on 2021-11-19 20:02

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Banner',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='created')),
                ('updated', models.DateTimeField(auto_now=True, verbose_name='updated')),
                ('title', models.CharField(max_length=100, verbose_name='title')),
                ('subtitle', models.CharField(max_length=100, verbose_name='subtitle')),
                ('content', models.CharField(max_length=255, verbose_name='content')),
                ('image', models.ImageField(null=True, upload_to='photos/')),
                ('url', models.CharField(max_length=255, verbose_name='title')),
                ('order', models.IntegerField(verbose_name='order')),
            ],
            options={
                'verbose_name': 'banner',
                'verbose_name_plural': 'banners',
                'ordering': ['order'],
            },
        ),
    ]
