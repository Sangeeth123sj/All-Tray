# Generated by Django 3.1.2 on 2020-10-27 18:19

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tray', '0013_store_store_balance'),
    ]

    operations = [
        migrations.RenameField(
            model_name='item',
            old_name='item1',
            new_name='item',
        ),
        migrations.RenameField(
            model_name='item',
            old_name='quantity1',
            new_name='quantity',
        ),
        migrations.RemoveField(
            model_name='item',
            name='item2',
        ),
        migrations.RemoveField(
            model_name='item',
            name='quantity2',
        ),
    ]
