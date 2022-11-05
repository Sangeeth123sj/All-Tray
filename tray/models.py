# from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import Model
import uuid
User = get_user_model()
import random
import string
from datetime import datetime
from django.core.files.storage import FileSystemStorage
from django.utils.timezone import now

# Create your models here.

BREAKS = (
    ("Now", "Now"),
    ("First Break", "First Break"),
    ("Lunch Break", "Lunch Break"),
    ("Last Break", "Last Break"),
)

BRANCHES = (
    ("Electronics & Communication", "Electronics & Communication"),
    ("Computer Science", "Computer Science"),
    ("Civil", "Civil"),
    ("Mechanical", "Mechanical"),
)

SEMESTERS = (
    ("semester 1", "semester 1"),
    ("semester 2", "semester 2"),
    ("semester 3", "semester 3"),
    ("semester 4", "semester 4"),
    ("semester 5", "semester 5"),
    ("semester 6", "semester 6"),
    ("semester 7", "semester 7"),
    ("semester 8", "semester 8"),
)

PLANS = (("basic", "basic"), ("standard", "standard"))


class Institute(models.Model):
    institute_name = models.CharField(max_length=200)
    institute_balance = models.IntegerField(default=0)
    plan = models.CharField(max_length=200, choices=PLANS, default="basic")
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="institute")
    identification_token = models.UUIDField(default=None, null=True, blank=True)
    fee_details = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    def __str__(self):
        return str(self.institute_name)



class InstituteMerchantCredentail(models.Model):
    # paytm creds
    paytm_merchant_id = models.CharField(max_length=200, null=True, blank=True)
    paytm_channel_id = models.CharField(max_length=200, null=True, blank=True)
    paytm_website = models.CharField(max_length=200, null=True, blank=True)
    paytm_industry_type = models.CharField(max_length=200, null=True, blank=True)
    paytm_secret_key = models.CharField(max_length=200, null=True, blank=True)
    college = models.OneToOneField(Institute, on_delete=models.CASCADE, related_name="merchant_creds")
    created_at = models.DateTimeField(auto_now_add=True,  null=True, blank=True)
        
    def __str__(self):
        return "Merchant creds of: " + str(self.college.institute_name) 



class Student(models.Model):
    name = models.CharField(max_length=200)
    branch = models.CharField(max_length=200, choices=BRANCHES)
    sem = models.CharField(max_length=200, choices=SEMESTERS)
    reg_no = models.CharField(max_length=200, blank=True)
    balance = models.IntegerField(default=0)
    pin_no = models.CharField(max_length=200, blank=True)
    college = models.ForeignKey(Institute, on_delete=models.CASCADE)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="student" )
    identification_token = models.UUIDField(default=None, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True,  null=True, blank=True)
    def __str__(self):
        return (
            "Student: "
            + str(self.name)
            + " | College: "
            + str(self.college.institute_name)
        )



class FeePayment(models.Model):
    # feepayment status of student on the institute
    paid_fee = models.IntegerField(default=0)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    institute = models.ForeignKey(Institute, on_delete=models.CASCADE,  null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True,  null=True, blank=True)
    
    def __str__(self):
        return("student: "+ str(self.student) + "paid fee: "+ str(self.paid_fee) +"college: "+str(self.institute)+ "day: "+ str(self.created_at.date()))


class Store(models.Model):
    store_name = models.CharField(max_length=200)
    store_status = models.BooleanField()
    store_details = models.CharField(max_length=300, blank=True)
    store_balance = models.IntegerField(default=0)
    invoice_code = models.CharField(max_length=2, blank=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    college = models.ForeignKey(Institute, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True,  null=True, blank=True)
    def __str__(self):
        return (
            "Store: "
            + str(self.store_name)
            + " | open:"
            + str(self.store_status)
            + " | college: "
            + str(self.college.institute_name)
        )


class Item(models.Model):
    item = models.CharField(max_length=200)
    stock = models.IntegerField(default=1)
    price = models.IntegerField(default=0)
    available = models.BooleanField(default=True)
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True,  null=True, blank=True)
    def __str__(self):
        return (
            "Item: "
            + str(self.item)
            + " | store:"
            + str(self.store.store_name)
            + " | college: "
            + str(self.store.college.institute_name)
        )


class OrderGroup(models.Model):
    # to find which time purchase the orders belong to
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    otp = models.CharField(max_length=4,null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True,  null=True, blank=True)
    order_group_total = models.IntegerField(default=0)
    def __str__(self):
        return("Store: "+ str(self.store) + "Student: "+ str(self.student) + "otp: "+ str(self.otp))

class Order(models.Model):
    item = models.CharField(max_length=200, blank=True)
    quantity = models.IntegerField(default=0)
    cost = models.IntegerField(default=0)
    pickup_time = models.CharField(max_length=200, choices=BREAKS)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True,  null=True, blank=True)
    status = models.BooleanField(default=False)
    otp = models.CharField(max_length=4)
    purchase_id = models.IntegerField(default=0)
    order_group = models.ForeignKey(OrderGroup, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return (
            "Item: "
            + str(self.item)
            + " | Pickuptime: "
            + str(self.pickup_time)
            + " | Student: "
            + str(self.student.name)
        )



class Revenue(models.Model):
    # to find the total revenue from the student for the day
    day_revenue = models.FloatField(default=0)
    total = models.IntegerField(default=0)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    institute = models.ForeignKey(Institute, on_delete=models.CASCADE,  null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True,  null=True, blank=True)
    
    def __str__(self):
        return("student: "+ str(self.student) + "day_revenue: "+ str(self.day_revenue) + "day: "+ str(self.created_at.date()))
    
class Subscription(models.Model):
    # show subscription details and payment status for subscription and revenue
    created_at = models.DateTimeField(auto_now_add=True)
    subscription_payment_status = models.BooleanField(default=False)
    revenue_payment_status = models.BooleanField(default=False)
    institute = models.ForeignKey(Institute, on_delete=models.CASCADE)

class SubscriptionPlans(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    basic = models.IntegerField(default=0)
    standard = models.IntegerField(default=1000)

class CartItem(models.Model):
    item = models.CharField(max_length=200, blank=True)
    quantity = models.IntegerField(default=0)
    cost = models.IntegerField(default=0)
    pickup_time = models.CharField(max_length=200, choices=BREAKS)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True,  null=True, blank=True)

    def __str__(self):
        return (
            "Item: "
            + str(self.item)
            + " | store:"
            + str(self.store.store_name)
            + " | college: "
            + str(self.store.college.institute_name)
        )


class Break(models.Model):
    first_break = models.TimeField(auto_now=False, auto_now_add=False, null=True)
    lunch_break = models.TimeField(auto_now=False, auto_now_add=False, null=True)
    last_break = models.TimeField(auto_now=False, auto_now_add=False, null=True)
    college = models.ForeignKey(Institute, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True,  null=True, blank=True)
    def __str__(self):
        return "Breaks of: " + str(self.college.institute_name)

# invoice storage location
# fs = FileSystemStorage()


class Bill(models.Model):
    item = models.CharField(max_length=200, blank=True)
    quantity = models.IntegerField(default=0)
    price = models.IntegerField(default=0)
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    invoice_no = models.SlugField(max_length=10)
    invoice = models.FileField(
        upload_to="django_field_pdf",
        max_length=254,
    )
    created_at = models.DateTimeField(auto_now_add=True,  null=True, blank=True)
    status = models.BooleanField(default=False)

    def __str__(self):
        return "Item: " + str(self.item) + " | Store: " + str(self.store.store_name)


class BulkRechargeMail(models.Model):
    email = models.EmailField(max_length=254)
    recharge_amount = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True,  null=True, blank=True)
    active = models.BooleanField(default=False)
    college = models.ForeignKey(Institute, on_delete=models.CASCADE)
    account_status = models.BooleanField(default=False)
    student = models.ForeignKey(Student, on_delete=models.CASCADE,  null=True, blank=True)
    def __str__(self):
        return "Bulk recharge: " + str(self.email) + " | status: " + str(self.active)
