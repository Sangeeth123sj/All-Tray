# Generated by Django 3.1.2 on 2021-11-21 08:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tray', '0010_bill_invoice_code'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bill',
            name='invoice_no',
            field=models.SlugField(max_length=10),
        ),
    ]
