# Generated by Django 4.0.6 on 2022-10-25 08:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tray', '0028_subscription'),
    ]

    operations = [
        migrations.CreateModel(
            name='SubscriptionPlans',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('basic', models.IntegerField(default=0)),
                ('standard', models.IntegerField(default=1000)),
            ],
        ),
    ]