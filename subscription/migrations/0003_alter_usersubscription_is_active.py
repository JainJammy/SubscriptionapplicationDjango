# Generated by Django 5.0.6 on 2024-08-01 14:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('subscription', '0002_alter_usersubscription_start_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usersubscription',
            name='is_active',
            field=models.BooleanField(default=False),
        ),
    ]
