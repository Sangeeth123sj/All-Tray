# Generated by Django 4.0.6 on 2022-11-04 09:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tray', '0034_institutemerchantcredentail_fee_details'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='institutemerchantcredentail',
            name='fee_details',
        ),
        migrations.AddField(
            model_name='institute',
            name='fee_details',
            field=models.TextField(blank=True, null=True),
        ),
    ]
