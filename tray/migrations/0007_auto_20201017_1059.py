# Generated by Django 3.1.2 on 2020-10-17 10:59

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tray', '0006_auto_20201017_1058'),
    ]

    operations = [
        migrations.RenameField(
            model_name='items',
            old_name='quantity',
            new_name='quantity1',
        ),
    ]
