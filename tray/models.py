from django.db import models
from django.db.models import Model
from django.contrib.auth.models import User
# Create your models here.

BREAKS = (  
    ('A', 'Now'),
    ('B', 'First Break'),
    ('C', 'Second Break'),
    ('D', 'LAst Break'),
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
    prize = models.IntegerField(default=0)
    store = models.ForeignKey(Store, on_delete=models.CASCADE)

class Order(models.Model):
    item1 = models.CharField(max_length=200, blank = True)
    quantity1 = models.IntegerField(default=0)
    cost1 = models.IntegerField(default=0)
    Time = models.CharField(max_length=200, choices=BREAKS)
    Student = models.ForeignKey(Student, on_delete=models.CASCADE)