# Generated by Django 3.1.2 on 2021-09-10 06:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tray', '0004_order_otp'),
    ]

    operations = [
        migrations.AlterField(
            model_name='student',
            name='name',
            field=models.CharField(max_length=200, unique=True),
        ),
        migrations.AlterField(
            model_name='student',
            name='pin_no',
            field=models.CharField(max_length=200),
        ),
        migrations.AlterField(
            model_name='student',
            name='reg_no',
            field=models.CharField(max_length=200),
        ),
    ]
