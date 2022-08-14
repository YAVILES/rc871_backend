# Generated by Django 4.0.5 on 2022-08-14 18:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('security', '0002_alter_role_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='document_type',
            field=models.CharField(choices=[('V', 'Venezolano'), ('E', 'Extranjero'), ('J', 'Jurídico')], default='V', max_length=10, verbose_name='document type'),
        ),
    ]