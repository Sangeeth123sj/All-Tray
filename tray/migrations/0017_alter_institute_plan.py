# Generated by Django 4.0.6 on 2022-10-20 15:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tray', '0016_student_identification_token'),
    ]

    operations = [
        migrations.AlterField(
            model_name='institute',
            name='plan',
            field=models.CharField(choices=[('basic', 'basic'), ('standard', 'standard')], default='basic', max_length=200),
        ),
    ]