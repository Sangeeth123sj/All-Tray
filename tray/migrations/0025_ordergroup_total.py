# Generated by Django 4.0.6 on 2022-10-23 13:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tray', '0024_revenue_total'),
    ]

    operations = [
        migrations.AddField(
            model_name='ordergroup',
            name='total',
            field=models.IntegerField(default=0),
        ),
    ]