# Generated by Django 3.1.2 on 2021-11-22 07:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tray', '0017_auto_20211122_1323'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bill',
            name='invoice',
            field=models.FileField(max_length=254, upload_to='django_field_pdf'),
        ),
    ]
