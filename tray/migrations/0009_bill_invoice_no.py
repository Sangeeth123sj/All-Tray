# Generated by Django 3.1.2 on 2021-11-21 08:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tray', '0008_auto_20211119_2232'),
    ]

    operations = [
        migrations.AddField(
            model_name='bill',
            name='invoice_no',
            field=models.IntegerField(default=0),
        ),
    ]
