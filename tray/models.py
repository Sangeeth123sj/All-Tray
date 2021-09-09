from django.db import models
from django.db.models import Model
from django.contrib.auth.models import User
from django.utils.timezone import now
from datetime import datetime
import string, random
# Create your models here.

BREAKS = (  
    ('Now', 'Now'),
    ('First Break', 'First Break'),
    ('Lunch Break', 'Lunch Break'),
    ('Last Break', 'Last Break'),
)

BRANCHES = (
    ('Electronics & Communication','Electronics & Communication'),
    ('Computer Science', 'Computer Science'),
    ('Civil','Civil'),
    ('Mechanical', 'Mechanical'),
)

SEMESTERS = (
    ('semester 1', 'semester 1'),
    ('semester 2', 'semester 2'),
    ('semester 3', 'semester 3'),
    ('semester 4', 'semester 4'),
    ('semester 5', 'semester 5'),
    ('semester 6', 'semester 6'),
    ('semester 7', 'semester 7'),
    ('semester 8', 'semester 8'),


)

class Institute(models.Model):
    institute_name = models.CharField(max_length=200)
    institute_balance = models.IntegerField(default=0)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    def __str__(self):
        return str(self.institute_name)
    
class Student(models.Model):
    name = models.CharField(max_length=200)
    branch = models.CharField(max_length=200, choices=BRANCHES)
    sem = models.CharField(max_length=200, choices=SEMESTERS)
    reg_no = models.CharField(max_length=200, unique = True)
    balance = models.IntegerField(default=0)
    pin_no = models.CharField(max_length=200, unique = True)
    college = models.ForeignKey(Institute, on_delete=models.CASCADE )
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    def __str__(self):
        return "Student: "+str(self.name)+" | College: "+ str(self.college.institute_name)
    
class Store(models.Model):
    store_name = models.CharField(max_length=200)
    store_status = models.BooleanField()
    store_details = models.CharField(max_length=300, blank = True)
    store_balance = models.IntegerField(default=0)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    college = models.ForeignKey(Institute, on_delete=models.CASCADE )
    def __str__(self):
        return "Store: "+str(self.store_name)+" | open:"+ str(self.store_status)+" | college: "+ str(self.college.institute_name)

class Item(models.Model):
    item = models.CharField(max_length=200)
    stock = models.IntegerField(default=1)
    price = models.IntegerField(default=0)
    available = models.BooleanField(default=True)
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    def __str__(self):
        return "Item: "+str(self.item)+" | store:"+ str(self.store.store_name)+" | college: "+ str(self.store.college.institute_name)

class Order(models.Model):
    item = models.CharField(max_length=200, blank = True)
    quantity = models.IntegerField(default=0)
    cost = models.IntegerField(default=0)
    pickup_time = models.CharField(max_length=200, choices=BREAKS)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.BooleanField(default=False)
    otp = models.CharField(max_length=4)
    def __str__(self):
        return "Item: "+str(self.item)+" | Pickuptime: "+ str(self.pickup_time)+" | Student: "+str(self.student.name)
            
class CartItem(models.Model):
    item = models.CharField(max_length=200, blank = True)
    quantity = models.IntegerField(default=0)
    cost = models.IntegerField(default=0)
    pickup_time = models.CharField(max_length=200, choices=BREAKS)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return "Item: "+str(self.item)+" | store:"+ str(self.store.store_name)+" | college: "+ str(self.store.college.institute_name)

class Break(models.Model):
    first_break = models.TimeField(auto_now=False, auto_now_add=False, null=True)
    lunch_break = models.TimeField(auto_now=False, auto_now_add=False, null=True)
    last_break = models.TimeField(auto_now=False, auto_now_add=False, null=True)
    college = models.ForeignKey(Institute, on_delete=models.CASCADE)
    def __str__(self):
        return "Breaks of: "+str(self.college.institute_name)