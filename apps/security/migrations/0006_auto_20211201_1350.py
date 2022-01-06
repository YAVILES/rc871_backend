# Generated by Django 3.1.2 on 2021-12-01 17:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('security', '0005_user_role'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='groups',
        ),
        migrations.RemoveField(
            model_name='user',
            name='role',
        ),
        migrations.RemoveField(
            model_name='user',
            name='user_permissions',
        ),
        migrations.AddField(
            model_name='user',
            name='roles',
            field=models.ManyToManyField(blank=True, help_text='The roles this user belongs to. A user will get all workflows granted to each of their roles.', related_name='user_set', related_query_name='user', to='security.Role', verbose_name='roles'),
        ),
        migrations.AddField(
            model_name='user',
            name='user_work_flows',
            field=models.ManyToManyField(blank=True, help_text='Specific work flows for this user.', related_name='user_set', related_query_name='user', to='security.Workflow', verbose_name='user work flows'),
        ),
        migrations.AlterField(
            model_name='user',
            name='is_superuser',
            field=models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status'),
        ),
    ]