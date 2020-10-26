from django.db import models
from django.db.models import Model
from django.contrib.auth.models import User
# Create your models here.

class Student(models.Model):
    name = models.CharField(max_length=200)
    reg_no = models.IntegerField(default=0)
    balance = models.IntegerField(default=0)

class Item(models.Model):
    item1 = models.CharField(max_length=200)
    quantity1 = models.IntegerField(default=1)

    item2 = models.CharField(max_length=200, blank = True)
    quantity2 = models.IntegerField(default=0)

class Store(models.Model):
    store_name = models.CharField(max_length=200)
    store_status = models.BooleanField()
    store_balance = models.IntegerField(default=0)
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.store_name)+" "+ str(self.store_status)