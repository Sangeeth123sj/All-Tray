# Generated by Django 4.0.6 on 2022-10-24 07:37

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tray', '0026_remove_ordergroup_total'),
    ]

    operations = [
        migrations.AddField(
            model_name='revenue',
            name='institute',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='tray.institute'),
        ),
    ]
