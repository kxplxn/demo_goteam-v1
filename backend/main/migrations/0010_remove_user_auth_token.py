# Generated by Django 3.1.7 on 2021-04-10 16:41

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0009_user_auth_token'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='auth_token',
        ),
    ]