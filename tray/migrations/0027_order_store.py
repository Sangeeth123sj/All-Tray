# Generated by Django 3.1.2 on 2020-11-02 18:18

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tray', '0026_order_student'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='store',
            field=models.ForeignKey(default=2, on_delete=django.db.models.deletion.CASCADE, to='tray.store'),
            preserve_default=False,
        ),
    ]