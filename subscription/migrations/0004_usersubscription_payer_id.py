# Generated by Django 5.0.6 on 2024-08-01 20:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('subscription', '0003_alter_usersubscription_is_active'),
    ]

    operations = [
        migrations.AddField(
            model_name='usersubscription',
            name='payer_id',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
