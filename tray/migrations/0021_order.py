# Generated by Django 3.1.2 on 2020-11-01 08:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tray', '0020_item_prize'),
    ]

    operations = [
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('item1', models.CharField(max_length=200)),
                ('quantity1', models.IntegerField(default=1)),
                ('prize1', models.IntegerField(default=0)),
                ('item2', models.CharField(blank=True, max_length=200)),
                ('quantity2', models.IntegerField(default=0)),
                ('prize2', models.IntegerField(default=0)),
                ('item3', models.CharField(blank=True, max_length=200)),
                ('quantity3', models.IntegerField(default=0)),
                ('prize3', models.IntegerField(default=0)),
                ('item4', models.CharField(blank=True, max_length=200)),
                ('quantity4', models.IntegerField(default=0)),
                ('prize4', models.IntegerField(default=0)),
                ('item5', models.CharField(blank=True, max_length=200)),
                ('quantity5', models.IntegerField(default=0)),
                ('prize5', models.IntegerField(default=0)),
            ],
        ),
    ]
