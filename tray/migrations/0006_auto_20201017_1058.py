# Generated by Django 3.1.2 on 2020-10-17 10:58

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tray', '0005_items_quantity2'),
    ]

    operations = [
        migrations.RenameField(
            model_name='items',
            old_name='item',
            new_name='item1',
        ),
    ]
