# Generated by Django 3.1.2 on 2022-06-02 11:28

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='payment',
            name='payment_date',
        ),
    ]