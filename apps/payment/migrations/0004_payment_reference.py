# Generated by Django 3.1.2 on 2022-06-02 11:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0003_auto_20220602_0735'),
    ]

    operations = [
        migrations.AddField(
            model_name='payment',
            name='reference',
            field=models.CharField(default='0001', max_length=255, verbose_name='reference'),
            preserve_default=False,
        ),
    ]
