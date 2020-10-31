from django.db import models
from django.db.models import Model
from django.contrib.auth.models import User
# Create your models here.

class Student(models.Model):
    name = models.CharField(max_length=200)
    reg_no = models.IntegerField(default=0)
    balance = models.IntegerField(default=0)

class Store(models.Model):
    store_name = models.CharField(max_length=200)
    store_status = models.BooleanField()
    store_balance = models.IntegerField(default=0)
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.store_name)+" "+ str(self.store_status)

class Item(models.Model):
    item = models.CharField(max_length=200)
    quantity = models.IntegerField(default=1)
    store = models.ForeignKey(Store, on_delete=models.CASCADE)