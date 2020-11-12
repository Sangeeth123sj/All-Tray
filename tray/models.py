from django.db import models
from django.db.models import Model
from django.contrib.auth.models import User
from django.utils.timezone import now
from datetime import datetime

# Create your models here.

BREAKS = (  
    ('Now', 'Now'),
    ('First Break', 'First Break'),
    ('Second Break', 'Second Break'),
    ('Last Break', 'LAst Break'),
)


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
    price = models.IntegerField(default=0)
    store = models.ForeignKey(Store, on_delete=models.CASCADE)

class Order(models.Model):
    item1 = models.CharField(max_length=200, blank = True)
    stock = models.IntegerField(default=0)
    cost1 = models.IntegerField(default=0)
    Time = models.CharField(max_length=200, choices=BREAKS)
    Student = models.ForeignKey(Student, on_delete=models.CASCADE)
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
