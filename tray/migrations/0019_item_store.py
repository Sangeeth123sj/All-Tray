# Generated by Django 3.1.2 on 2020-10-27 18:49

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tray', '0018_auto_20201027_1847'),
    ]

    operations = [
        migrations.AddField(
            model_name='item',
            name='store',
            field=models.ForeignKey(default=2, on_delete=django.db.models.deletion.CASCADE, to='tray.store'),
            preserve_default=False,
        ),
    ]
