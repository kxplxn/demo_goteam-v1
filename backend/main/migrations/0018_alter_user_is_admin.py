# Generated by Django 3.2.2 on 2021-05-12 10:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0017_auto_20210511_1542'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='is_admin',
            field=models.BooleanField(db_index=True, default=False),
        ),
    ]
