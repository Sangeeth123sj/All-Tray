from django.db import models
from django.db.models import Model
# Create your models here.

class Student(models.Model):
    name = models.CharField(max_length=200)
    reg_no = models.IntegerField(default=0)
    
class Items(models.Model):
    item = models.CharField(max_length=200)
    quantity = models.IntegerField(default=0)