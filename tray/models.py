from django.db import models
from django.db.models import Model
# Create your models here.

class Student(models.Model):
    name = models.CharField(max_length=200)
    reg_no = models.IntegerField(default=0)
    balance = models.IntegerField(default=0)
class Items(models.Model):
    item1 = models.CharField(max_length=200)
    quantity1 = models.IntegerField(default=1)

    item2 = models.CharField(max_length=200, blank = True)
    quantity2 = models.IntegerField(default=0)