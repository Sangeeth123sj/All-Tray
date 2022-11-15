# from django.contrib.auth.models import User
from logging import exception
from django.contrib.auth import authenticate, get_user_model, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404, redirect, render
from datetime import time
import time
from dateutil.relativedelta import relativedelta
from django.db.models import Sum
from django.urls import reverse
import string
import random
import razorpay
from django.conf import settings
import uuid
from django.contrib.auth.hashers import check_password
from django.core.paginator import Paginator

from .models import (
    InstituteEvent,
    Bill,
    Break,
    BulkRechargeMail,
    CartItem,
    FeePayment,
    Institute,
    Item,
    Order,
    Store,
    Student,
    User,
    InstituteMerchantCredentail,
    OrderGroup,
    Revenue,
    Subscription,
    SubscriptionPlans
)

User = get_user_model()
setattr(User, 'backend', 'tray.backend.MyBackend')
import json
import random
import string
from datetime import date, datetime, timedelta

# import checksum generation utility
# You can get this utility from https://developer.paytm.com/docs/checksum/
import paytmchecksum
import requests
from django.contrib import messages
from django.contrib.auth.hashers import check_password, make_password
from django.core.files.base import File
from django.http import FileResponse, JsonResponse
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

from .modules.invoice import *

# student views______________________________________________________________________________

def index(request):
    return render(request, "tray/login_base.html")

def homepage_layout(request):
    return render(request, "tray/homepage_layout.html")

def register_card(request):
    colleges = Institute.objects.all()
    return render(request, "tray/register_card.html", {"colleges": colleges})


def register_card_post(request):
    if request.method == "POST":
        student_name = request.POST.get("student_name")
        branch = request.POST.get("branch_name")
        semester = request.POST.get("semester")
        password = request.POST.get("password")
        card_pin = request.POST.get("card_pin")
        college_id = request.POST.get("college_id")
        email = request.POST.get("mail_id")
        college_object = Institute.objects.get(id=college_id)
        user = User.objects.create_user(email, password)
        user.save
        student = Student(
            name=student_name,
            branch=branch,
            sem=semester,
            college=college_object,
            user=user,
        )
        if card_pin:
            student.pin_no = card_pin
        student.save()
        if BulkRechargeMail.objects.filter(email=email).exists():
            student_bulk_recharge_objects = BulkRechargeMail.objects.filter(email=email)
            for bulk_recharge_object in student_bulk_recharge_objects:
                student.balance = int(student.balance) +  int(bulk_recharge_object.recharge_amount)
                bulk_recharge_object.active = True
                bulk_recharge_object.account_status = True
                bulk_recharge_object.student = student
                student.save()
                bulk_recharge_object.save()
        messages.success(request, "Profile created.")
        return render(request, "tray/entry.html")


def entry(request):
    if request.user.is_authenticated:
        student_user = Student.objects.filter(user=request.user).exists()
        store_user = Store.objects.filter(user=request.user).exists()
        college_user = Institute.objects.filter(user=request.user).exists()
        if student_user:
            print("Already logged in student")
            return redirect("home")
        if store_user:
            print("Already logged in store")
            return redirect("store_home")
        if college_user:
            print("Already logged in college")
            return redirect("college_home")
        else:
            return render(request, "tray/entry.html")
    else:
        return render(request, "tray/entry.html")

@csrf_exempt 
# exempting csrf is temporary fix
def home_post(request):
    if request.method == "POST":
        email = request.POST["email"]
        password = request.POST["password"]
        request.session["email"] = email
        request.session["password"] = password
        user = authenticate(request, email=email, password=password)
        print("user",user)
        if user is None:
            return redirect("entry")
        login(request, user)
        print("Student " + str(user) + " just logged in")
        return redirect(home)


@login_required
def home(request):
    if request.user.is_authenticated:
        user = request.user
        student_user = Student.objects.filter(user=request.user).exists()
        store_user = Store.objects.filter(user=request.user).exists()
        college_user = Institute.objects.filter(user=request.user).exists()
    if student_user:
        stores = Store.objects.filter(college=user.student.college)
        student = user.student
        request.session["student_id"] = student.id
        print("logged in student")
        return render(request, "tray/home.html", {"stores": stores, "student": student})
    elif store_user:
        print("logged in store")
        store_id = user.store.id
        request.session["store_id"] = store_id
        return redirect("store_home")
    elif college_user:
        institute_id = user.institute.id
        request.session["institute_id"] = institute_id
        print("logged in college")
        return redirect("college_home")
    else:
        c = "Sorry login failed! you're just a user, not a student or store or college!"
        return HttpResponse(c)


@login_required
def student_profile(request):
    student = request.user.student
    context = {
        "student":student
    }
    return render(request, "tray/student_profile.html", context)




@login_required
def college_edit_details(request):
    if request.method == "POST":
        institute = request.user.institute
        name = request.POST.get("name")
        institute.institute_name = name
        institute.save()
        print(institute, "edit saved")
        return redirect("college_home")
    
    institute = request.user.institute
    context = {
        "institute":institute
    }
    return render(
        request,
        "tray/college_edit_details.html",
        context
    )

@login_required
def college_payment_creds_edit(request):
    institute = request.user.institute
    try:
        payment_creds = InstituteMerchantCredentail.objects.get(college=institute)
    except:
        payment_creds = None
    context = {"payment_creds":payment_creds}
    return render(request, "tray/college_merchant_creds_form.html",context)

@login_required
def college_edit_validate(request):
    name = request.GET.get("name")
    present_name = request.user.institute.institute_name
    institute_present = Institute.objects.filter(institute_name=name).exclude(institute_name=present_name).exists()
    data = {"institute_taken": institute_present}
    return JsonResponse(data)


@login_required
def student_edit_details(request):
    if request.method == "POST":
        student = request.user.student
        name = request.POST.get("name")
        branch = request.POST.get("branch")
        semester = request.POST.get("semester")
        card = request.POST.get("card")
        student.name = name
        student.branch = branch
        student.sem = semester
        student.pin_no = card
        student.save()
        print(student, "saved")
        return redirect("home")
    
    student = request.user.student
    context = {
        "name": student.name,
        "branch":student.branch,
        "semester":student.sem,
        "card":student.pin_no
    }
    return render(
        request,
        "tray/student_edit_details.html",
        context
    )


@login_required
def your_orders_post(request):
    if request.method == "POST":
        student_id = request.POST["student_id"]
        request.session["student_id"] = student_id
        return redirect(your_orders)


@login_required
def your_orders(request):
    student_object = request.user.student
    print(request.user.student)
    orders = Order.objects.filter(student=student_object)
    sorted_orders = orders.order_by("-created_at")
     # pagination logic
    page = request.GET.get('page')
    orders_paginated = Paginator(sorted_orders, 20)
    if page is None:
        page_order_list = orders_paginated.page(1)
    else:
        page_order_list = orders_paginated.page(page)
    order_exist = Order.objects.filter(student=student_object).exists()
    if order_exist:
        otp = orders.first().otp
    else:
        otp = ""
    return render(request, "tray/your_orders.html", {"orders": sorted_orders, "order_list":page_order_list,  "otp": otp})


@login_required
def order_page_post(request):
    if request.method == "POST":
        student_id = request.POST["student_id"]
        store_id = request.POST["store_id"]
        request.session["student_id"] = student_id
        request.session["store_id"] = store_id
        return redirect(order_page)
    else:
        c = "Sorry login failed!"
        return HttpResponse(c)


@login_required
def order_page(request):
    # student_id = request.session["student_id"]
    store_id = request.session["store_id"]
    # student = Student.objects.get(id=student_id)
    student = request.user.student
    college = student.college
    store = Store.objects.get(id=store_id)
    items = store.item_set.filter(available=True)
    # college_free_trial_expiry_date_in_milliseconds = int(time.mktime((college.created_at+relativedelta(months=2)).timetuple())) * 1000
    return render(
        request,
        "tray/order_page.html",
        {"student": student, "store": store, "college": college, "items": items,}
    )


@login_required
def student_pin_edit(request):
    # student_id = request.session["student_id"]
    # student = Student.objects.get(id=student_id)
    student = request.user.student
    return render(request, "tray/student_pin_edit.html", {"student": student})


@login_required
def student_pin_edit_post(request):
    # student_id = request.session["student_id"]
    if request.method == "POST":
        student = request.user.student
        password = request.POST["password"]
        # student = Student.objects.get(id=student_id)
        u = student.user
        u.set_password(password)
        u.save()
        logout(request)
        return redirect(entry)


@login_required
def student_logout(request):
    logout(request)
    return redirect("entry")


# store views_______________________________________________________________________________




def open_store(request):
    colleges = Institute.objects.all()
    return render(request, "tray/open_store.html", {"colleges": colleges})


def open_store_success(request):
    if request.method == "POST":
        college_id = request.POST["college_id"]
        institute = Institute.objects.get(id=college_id)
        username = request.POST["username"]
        store_name = request.POST["store_name"]
        store_details = request.POST["store_description"]
        email = request.POST["email"]
        password = request.POST["password"]
        user = User.objects.create_user(email, password)
        user.save
        store = Store(
            store_name=store_name,
            store_status=True,
            store_details=store_details,
            college=institute,
            user=user,
        )
        store.save()
        return redirect("entry")


def store_login(request):
    if request.user.is_authenticated:
        store_user = Store.objects.filter(user=request.user).exists()
        if store_user:
            print("Already logged in store")
            return redirect("store_home")
        else:
            return render(request, "tray/login_store.html")
    else:
        return render(request, "tray/login_store.html")


def store_login_processing(request):
    username = request.POST["username"]
    password = request.POST["password"]
    user = authenticate(request, username=username, password=password)

    if user is not None:
        logout(request)
        login(request, user)
        store_id = user.store.id
        request.session["store_id"] = store_id
        return redirect("store_home")
    else:
        c = "Sorry login failed!"
        return HttpResponse(c)



@login_required
def store_profile(request):
    store = request.user.store
    context = {
        "store":store
    }
    return render(request, "tray/store_profile.html", context)

@login_required
def user_edit(request):
    # common user edit method
    if request.method == "POST":
        email = request.POST.get("email")
        user = request.user
        user.email = email
        user.save()
        student_user = Student.objects.filter(user=user).exists()
        if student_user:
            return redirect("home")
        store_user = Store.objects.filter(user=user).exists()
        if store_user:
            return redirect("store_home")
        college_user = Institute.objects.filter(user=user).exists()
        if college_user:
            return redirect("college_home")
        
    user = request.user
    context = {
        "user": user
    }
    return render(request, "tray/user_edit.html", context)
    
@login_required
def store_home(request):
    # store_id = request.session["store_id"]
    # store = Store.objects.get(id=store_id)
    store = request.user.store
    store_name = store.store_name
    items = store.item_set.all()
     # pagination logic
    page = request.GET.get('page')
    items_paginated = Paginator(items, 20)
    if page is None:
        page_items = items_paginated.page(1)
    else:
        page_items = items_paginated.page(page)

    status = store.store_status
    if status == True:
        c = "Open"
    else:
        c = "Closed"
    return render(
        request,
        "tray/store_home.html",
        {
            "store": store,
            "store_name": store_name,
            "store_id": store.id,
            "status": c,
            "items": page_items,
        },
    )


@login_required
def store_billing(request):
    # store_id = request.session["store_id"]
    # store = Store.objects.get(id=store_id)
    store = request.user.store
    print("entering billing store: " + str(store))
    store_name = store.store_name
    items = store.item_set.filter(available=True)
    context = {"store": store, "store_name": store_name, "items": items}
    return render(request, "tray/store_billing.html", context)


@login_required
def billing_item_price(request):
    item_name = request.GET["item_name"]
    # store_id = request.GET["store_id"]
    # store = Store.objects.get(id = store_id)
    store = request.user.store
    item = Item.objects.get(item=item_name, store=store)
    item_price = item.price
    data = {
        "item_price": item_price,
    }
    return JsonResponse(data)


def invoice_number_gen(store):
    last_bill = Bill.objects.filter(store=store).order_by("id").last()
    # print('last bill ' + str(last_bill.invoice_no))
    if last_bill:
        last_invoice_no = last_bill.invoice_no
        # invoice number format is 'customer_name_short + number' eg: CS003
        last_invoice_initials = last_invoice_no[:2]
        last_invoice_digits = last_invoice_no[2:]
        new_invoice_digits = int(last_invoice_digits) + 1
        new_invoice_no = last_invoice_initials + str(new_invoice_digits)
    else:
        new_invoice_no = store.invoice_code + "01"
    return new_invoice_no


@login_required
def billing_invoice(request):
    store = request.user.store
    store_name = store.store_name
    load = json.loads(request.GET["order_list_json"])
    total = request.GET["total"]
    cash_or_card = request.GET["cash_or_card"]
    device = request.GET["device"]
    if cash_or_card == "card":
        pin_no = request.GET["pin_no"]
        student_check = Student.objects.filter(pin_no=pin_no).exists()
        print("student check " + str(student_check))
        if student_check == False:
            print("entered card false response")
            data = {"card_status": "card_invalid"}
            return JsonResponse(data)

        elif student_check == True:
            student = get_object_or_404(Student, pin_no=pin_no)
            if int(student.balance) < int(total):
                data = {"card_status": "low_balance"}
                return JsonResponse(data)
            
    request.session["device"] = device
    # generating incremented invoice no

    new_invoice_no = invoice_number_gen(store)

    # load is the list of orders
    # creating innvoice pdf
    create_invoice(store_name, new_invoice_no, load, total)
    # preparing invoice file for Bill db
    f = open("media/pdf/" + new_invoice_no, "rb")
    file = File(f)
    # creating bill orders on db
    objects = []
    new_object = []
    # assigning invoice number and other details
    if cash_or_card == "card":
        order_group = OrderGroup(store = store, student = student, order_group_total=0)
    else:
        order_group = OrderGroup(store = store, order_group_total=0)

    for i in load:
        if cash_or_card == "card":
            student = get_object_or_404(Student, pin_no=pin_no)
            new_object = Bill(
                item=i["item"],
                price=i["price"],
                quantity=i["quantity"],
                invoice_no=new_invoice_no,
                invoice=file,
                store=store,
                student=student
            )
        else:
             new_object = Bill(
                item=i["item"],
                price=i["price"],
                quantity=i["quantity"],
                invoice_no=new_invoice_no,
                invoice=file,
                store=store,
            )
        # creating order groups for tracking revenue
        order_group.order_group_total += (i["price"]*i["quantity"])
        order_group.save()
        institute=store.college
        free_trial_expiry_date = institute.created_at.date() + relativedelta(months=2)
        if date.today() < free_trial_expiry_date:
            # conditional block to calculate revenue after free trial
            try:
                if cash_or_card == "card":
                    revenue = Revenue.objects.filter(created_at__date=date.today(), student = student, institute=institute).first()
                    revenue.total = revenue.total + order_group.order_group_total
                    revenue.day_revenue = revenue.total * 0.01
                    revenue.save()
                    print("incrementing revenue", revenue.day_revenue, "present revenue:",revenue.day_revenue)
            except:
                if cash_or_card == "card":
                    day_order_groups_total = OrderGroup.objects.filter(created_at__date=date.today(),student=student).aggregate(Sum('order_group_total'))
                    print("group total",day_order_groups_total)
                    revenue = Revenue.objects.create(total=int(day_order_groups_total["order_group_total__sum"]), day_revenue= float(day_order_groups_total["order_group_total__sum"] *0.01), student = student,institute=institute)
        objects.append(new_object)
        item = Item.objects.get(item=i["item"])
        # initializing stock of item variable
        item_stock = item.stock
        # updating stock at store
        item.stock = int(item_stock) - int(i["quantity"])
        item.save()
        # unticking item availability to customers on reaching low stock at store
        if item.stock < 5:
            item.available = False
            item.save()
        if cash_or_card == "card":
            # updating store balance
            cost = i["quantity"] * i["price"]
            store.store_balance = store.store_balance + cost
            store.save()
            # updating student balance
            student.balance = student.balance - cost
            student.save()
    Bill.objects.bulk_create(objects)

    print(store_name)
    # print(load[0]["item"])
    request.session["invoice_name"] = new_invoice_no

    data = {"card_status":"transaction_completed"}
    return JsonResponse(data)


@login_required
def invoice_print(response):
    device = response.session["device"]
    invoice_name = response.session["invoice_name"]
    pdf = open("media/pdf/" + invoice_name, "rb")
    # device specific print or download
    if device == "desktop":
        response = FileResponse(pdf, content_type="application/pdf")
        response["Content-Disposition"] = "inline"

    elif device == "mobile":
        response = FileResponse(pdf)
        response["Content-Disposition"] = 'attachment; filename= "' + invoice_name + '"'
    return response


@login_required
def store_edit_details(request):
    # store_id = request.session["store_id"]
    store_object = request.user.store
    college_object = store_object.college
    return render(
        request,
        "tray/store_edit_details.html",
        {"store": store_object, "college": college_object},
    )


@login_required
def store_edit_details_post(request):
    if request.method == "POST":
        # store_id = request.session["store_id"]
        store_name = request.POST["store_name"]
        store_details = request.POST["store_description"]
        # store_object = Store.objects.get(id=store_id)
        store_object = request.user.store
        store_object.store_name = store_name
        store_object.store_details = store_details
        store_object.save()
    return redirect(store_home)


@login_required
def store_add_item(request):
    store_id = request.session["store_id"]
    return render(request, "tray/store_add_item.html", {"store_id": store_id})


@login_required
def store_add_item_save(request):
    if request.method == "POST":
        # store_id = request.session["store_id"]
        item_name = request.POST["item_name"]
        stock = request.POST["stock"]
        price = request.POST["price"]
        # store_object = Store.objects.get(id=store_id)
        store_object = request.user.store
        if int(stock) <=5 :
            available = False
        else:
            available = True
        new_item = Item(item=item_name, stock=stock,available=available, price=price, store=store_object)
        new_item.save()
    return redirect(store_home)


@login_required
def edit_items_post(request):
    if request.method == "POST":
        item_id = request.POST["item_id"]
        store_id = request.POST["store_id"]
        request.session["store_id"] = store_id
        request.session["item_id"] = item_id
        return redirect(edit_items)


@login_required
def edit_items(request):
    store_id = request.session["store_id"]
    item_id = request.session["item_id"]
    item = Item.objects.get(id=item_id)
    return render(
        request, "tray/edit_store_items.html", {"item": item, "store_id": store_id}
    )


@login_required
def edit_item_save(request):
    if request.method == "POST":
        item_id = request.POST["item_id"]
        edited_item_name = request.POST["item_name"]
        edited_stock = request.POST["stock"]
        edited_price = request.POST["price"]
        edited_item = Item.objects.get(id=item_id)
        edited_item.item = edited_item_name
        edited_item.stock = edited_stock
        edited_item.price = edited_price
        edited_item.save()
    return redirect(store_home)


def store_logout(request):
    logout(request)
    return redirect("entry")


@login_required
def store_order_list(request):
    # store_id = request.session["store_id"]
    # store_object = Store.objects.get(id=store_id)
    store_object = request.user.store
    orders = Order.objects.filter(store=store_object)
    sorted_orders = orders.order_by("-created_at")
     # pagination logic
    page = request.GET.get('page')
    orders_paginated = Paginator(sorted_orders, 20)
    if page is None:
        page_order_list = orders_paginated.page(1)
    else:
        page_order_list = orders_paginated.page(page)
    current_month = datetime.today().strftime("%h")
    current_month_number = datetime.today().month
    # month_total = orders.filter(created_at__month = current_month_number ).aggregate(Sum('cost'))
    month_orders = orders.filter(created_at__month=current_month_number)
    month_total = 0
    for order in month_orders:
        total = order.cost * order.quantity
        month_total = month_total + total
    print(page_order_list)
    return render(
        request,
        "tray/store_order_list.html",
        {
            "order_list": page_order_list,
            "page_order_object":page_order_list,
            "current_month": current_month,
            "month_total": month_total,
        },
    )


@login_required
def store_item_pickup(request):
    store = request.user.store
    first_break_orders = Order.objects.filter(store=store,status=False, pickup_time="First Break", created_at__date=date.today()).count()
    lunch_break_orders = Order.objects.filter(store=store,status=False, pickup_time="Lunch Break", created_at__date=date.today()).count()
    last_break_orders = Order.objects.filter(store=store,status=False, pickup_time="Last Break", created_at__date=date.today()).count()
    other_orders = Order.objects.filter(store=store,status=False, pickup_time="Now", created_at__date=date.today()).count()
    context = {
        "first_break_orders":first_break_orders,
        "lunch_break_orders":lunch_break_orders,
        "last_break_orders":last_break_orders,
        "other_orders":other_orders
    }
    return render(request, "tray/store_item_pickup.html",context)


@login_required
def store_item_pickup_validate(request):
    store = request.user.store
    otp = request.GET.get("otp")
    card = request.GET.get("card")
    print("otp: " + str(otp))
    print("card: " + str(card))
    if otp:
        check_otp = Order.objects.filter(
            otp=otp, store=store, created_at__date=date.today()
        ).exists()
        print("check otp " + str(check_otp))
        if check_otp:
            request.session["otp_or_card_selected"] = "otp"
            data = {
                "incorrect_status": "correct_otp",
            }
            return JsonResponse(data)
        else:
            data = {
            "incorrect_status": "incorrect_otp",
        }
        return JsonResponse(data)
    
    if card:
        check_student_valid = Student.objects.filter(pin_no=card).exists()
        print("check student: " + str(check_student_valid))
        if check_student_valid:
            student = Student.objects.get(pin_no=card)
            check_card = Order.objects.filter(
                student=student, created_at__date=date.today()
            ).exists()
        else:
            check_card = False
            
    if check_card:
        request.session["otp_or_card_selected"] = "card"
        data = {"incorrect_status": "correct_card"}
        return JsonResponse(data)
    else:
        data = {
            "incorrect_status": "incorrect_card",
        }
        return JsonResponse(data)


@login_required
def user_pickup_orders_post(request):
    if request.method == "POST":
        otp= request.POST.get("otp")
        card= request.POST.get("pin_no")
        if card:
            request.session["otp_or_card"] = card
        if otp:
            request.session["otp_or_card"] = otp
        return redirect(user_pickup_orders)


@login_required
def user_pickup_orders(request):
    # store_id = request.session["store_id"]
    otp_or_card = request.session["otp_or_card"]
    otp_or_card_selected = request.session["otp_or_card_selected"]
    print("otp/card: " + otp_or_card_selected)
    if otp_or_card_selected == "otp":
        # store_object = Store.objects.get(id = store_id)
        orders = Order.objects.filter(otp=otp_or_card)
        return render(request, "tray/user_pickup_orders.html", {"orders": orders})
    elif otp_or_card_selected == "card":
        check_student = Student.objects.get(pin_no=otp_or_card)
        print("check student: " + str(check_student))
        orders = Order.objects.filter(student=check_student)
        print(str(orders))
        return render(request, "tray/user_pickup_orders.html", {"orders": orders})


@login_required
def store_bills(request):
    # store_id = request.session["store_id"]
    # store_object = Store.objects.get(id=store_id)
    store_object = request.user.store
    orders = Bill.objects.filter(store=store_object)
    sorted_orders = orders.order_by("-created_at")
     # pagination logic
    page = request.GET.get('page')
    orders_paginated = Paginator(sorted_orders, 20)
    if page is None:
        page_order_list = orders_paginated.page(1)
    else:
        page_order_list = orders_paginated.page(page)
    current_month = datetime.today().strftime("%h")
    current_month_number = datetime.today().month
    # month_total = orders.filter(created_at__month = current_month_number ).aggregate(Sum('cost'))
    month_orders = orders.filter(created_at__month=current_month_number)
    month_total = 0
    
    for order in month_orders:
        total = order.price * order.quantity
        month_total = month_total + total
    context = {
        "current_month":current_month,
        "month_total":month_total,
        "store": store_object,
        "order_list": page_order_list,
        "page_order_list":page_order_list
    }
    return render(
        request,
        "tray/store_bills.html",
        context
    )


def qr_code(request):
    return render(request, "tray/qr_code.html")


# college views__________________________________________________________________________________

def register_college(request):
    return render(request, "tray/register_college.html")


def register_college_success(request):
    if request.method == "POST":
        college = request.POST["college_name"]
        first_break = request.POST["first_break"]
        lunch_break = request.POST["lunch_break"]
        last_break = request.POST["last_break"]
        username = request.POST["username"]
        email = request.POST["email"]
        password = request.POST["password"]
        # plan = request.POST.get("plan_type",None)
        user = User.objects.create_user(email, password)
        user.save()
        institute = Institute(
            institute_name=college,
            user=user,
            # plan= "basic",
        )
        institute.save()
        break_time = Break(
            first_break=first_break,
            lunch_break=lunch_break,
            last_break=last_break,
            college=institute,
        )
        break_time.save()
        return redirect("entry")


def login_college(request):
    if request.user.is_authenticated:
        college_user = Institute.objects.filter(user=request.user).exists()
        if college_user:
            print("Already logged in")
            return redirect("college_home")

    else:
        return redirect("entry")


def college_profile(request):
    institute = request.user.institute
    try:
        payment_credential = InstituteMerchantCredentail.objects.get(college=institute)
    except:
        payment_credential = None
    try:
        break_object = Break.objects.get(college=institute)
    except:
        break_object = None
    context = {
        "institute":institute,
        "payment_credential":payment_credential,
        "break":break_object
    }
    return render(request,"tray/college_profile.html",context)

def college_login_verify(request):
    username = request.POST["username"]
    password = request.POST["password"]
    user = authenticate(request, username=username, password=password)
    user_institute_exist = Institute.objects.filter(user=user).exists()

    if user is not None and user_institute_exist:
        login(request, user)
        institute_id = user.institute.id
        request.session["institute_id"] = institute_id
        return redirect(college_home)
    else:
        c = "Sorry login failed!"
        return HttpResponse(c)


@login_required
def college_home(request):
    # institute_id = request.session.get("institute_id")
    print("_________",request.user.institute)
    # college = Institute.objects.get(id=institute_id)
    college = request.user.institute
    try:
        merchant_credentials = InstituteMerchantCredentail.objects.get(college=college)
    except InstituteMerchantCredentail.DoesNotExist:
        merchant_credentials = None
    print("mc:",merchant_credentials)
    try:
        subscription = Subscription.objects.get(institute=college)
    except Subscription.DoesNotExist:
        subscription = None
    except Subscription.MultipleObjectsReturned:
        subscription = Subscription.objects.filter(institute=college).first()
        print("multiple subscriptions for this college")
    request.session["college_id"] = college.id
    stores = Store.objects.filter(college=college)
    context = {"college": college, "stores": stores, "merchant_credentials": merchant_credentials, "subscription":subscription}
    return render(
        request, "tray/college_home.html", context
    )


@login_required
def college_subscription_form(request):
    if request.method == "GET":
        return render(request, "tray/college_subscription_form.html")
    if request.method == "POST":
        # institute_id = request.session.get("institute_id")
        # college = Institute.objects.get(id=institute_id)
        college = request.user.institute
        college.identification_token = uuid.uuid4()
        college.save()
        global client
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

        subscription_response = client.subscription.create({
            'plan_id': settings.BASIC_PLAN_ID,
            'customer_notify': 1,
            'quantity': 1,
            'total_count': 6,
            'addons': [{'item': {'name': 'Student revenue', 'amount': 100,
                    'currency': 'INR'}}],
            'notes': {'institute': college.institute_name}
            })
        print("subscription_response-----",subscription_response)
        subscription_id = subscription_response["id"]
        request.session["subscription_id"] = subscription_id
        basic_cost = SubscriptionPlans.basic
        standard_cost = SubscriptionPlans.objects.first().standard
        
        context = {"basic_cost":basic_cost, "standard_cost":standard_cost, "institute": college,
                "subscription_id": subscription_id, "key_id": settings.RAZORPAY_KEY_ID,
                "callback_url":settings.SUBSCRIPTION_CALLBACK_URL,"key_secret": settings.RAZORPAY_KEY_SECRET}
        print("rendering checkout")
        
    return render(request, "tray/college_subscription_checkout.html",context)

@login_required
def college_subscription_checkout(request):
    return render(request, "tray/college_subscription_checkout.html")


@csrf_exempt
def college_subscription_callback(request,institute_token, subscription_id):
    if request.method == 'POST':
        institute_token_decoded = uuid.UUID(institute_token).hex
        print("secret key",institute_token)
        print("secret key decoded",institute_token_decoded)
        institute = Institute.objects.get(identification_token=institute_token_decoded)
        print(request.body)
        print(request.POST)
        received_data = dict(request.POST)
        razorpay_signature = received_data.get('razorpay_signature')[0]
        razorpay_payment_id = received_data.get('razorpay_payment_id')[0]
        print("received callback DATAAAA:",received_data)
        # checking authenticity of callback response
        result = client.utility.verify_subscription_payment_signature({
            'razorpay_subscription_id': subscription_id,
            'razorpay_payment_id': razorpay_payment_id,
            'razorpay_signature': razorpay_signature
            })
        
        if result:
            Subscription.objects.create(subscription_payment_status=True,revenue_payment_status=True,institute=institute)
        context = {
            "result" : result
        }
        return render(request, "tray/college_subscription_callback.html", context)




def receipt_number_generator():
    # initializing size of string
    N = 7
 
    # using random.choices()
    # generating random strings
    res = ''.join(random.choices(string.ascii_uppercase +
                                string.digits, k=N))
    return str(res)
    
@login_required
def college_bulk_recharge(request):
    # college_id = request.session.get("college_id")
    # institute = Institute.objects.get(id = college_id)
    institute = request.user.institute
    college_bulk_recharge_list = BulkRechargeMail.objects.filter(college=institute)
    
    # pagination logic
    page = request.GET.get('page')
    orders_paginated = Paginator(college_bulk_recharge_list, 10)
    if page is None:
        page_college_bulk_recharge_list = orders_paginated.page(1)
    else:
        page_college_bulk_recharge_list = orders_paginated.page(page)
    context = {"institute": institute, "college_bulk_recharge_list": page_college_bulk_recharge_list}
    return render(request, "tray/college_bulk_recharge.html", context)

@login_required
def college_merchant_creds_form(request):
    if request.method == "GET":
        return render(request, "tray/college_merchant_creds_form.html")
    if request.method == "POST":
        paytm_merchant_id = request.POST.get("paytm_merchant_id")
        paytm_secret_key = request.POST.get("paytm_secret_key")
        paytm_website = request.POST.get("paytm_website")
        paytm_channel_id = request.POST.get("paytm_channel_id")
        paytm_industry_type = request.POST.get("paytm_industry_type")
        college = request.user.institute
        # college_id = request.session["college_id"]
        # college = Institute.objects.get(id= college_id)
        
        try:
            InstituteMerchantCredentail.objects.update_or_create(
            college=college,
            defaults={
                "paytm_merchant_id":paytm_merchant_id,
                "paytm_secret_key":paytm_secret_key,
                "paytm_website":paytm_website,
                "paytm_channel_id":paytm_channel_id,
                "paytm_industry_type":paytm_industry_type
            }
            )
            return redirect(college_home)
        except:
            print(exception)
            print("entered except")
            return render(request,"tray/college_merchant_creds_form.html", context={'error': 'Wrong Credentials please contact support'})


@login_required
def college_store_order_list_post(request):
    if request.method == "POST":
        store_id = request.POST["store_id"]
        request.session["store_id"] = store_id
        return redirect(college_store_order_list)


@login_required
def college_store_order_list(request):
    store_id = request.session["store_id"]
    store_object = Store.objects.get(id=store_id)
    orders = Order.objects.filter(store=store_object)
    sorted_orders = orders.order_by("-created_at")
     # pagination logic
    page = request.GET.get('page')
    orders_paginated = Paginator(sorted_orders, 20)
    if page is None:
        page_order_list = orders_paginated.page(1)
    else:
        page_order_list = orders_paginated.page(page)
    current_month = datetime.today().strftime("%h")
    current_month_number = datetime.today().month
    # month_total = orders.filter(created_at__month = current_month_number ).aggregate(Sum('cost'))
    month_orders = orders.filter(created_at__month=current_month_number)
    month_total = 0
    
    revenue_month_total = 0
    for order in month_orders:
        total = order.cost * order.quantity
        month_total = month_total + total

    return render(
        request,
        "tray/college_store_order_list.html",
        {
            "orders": sorted_orders,
            "page_order_list":page_order_list,
            "store": store_object,
            "current_month": current_month,
            "month_total": month_total,
        },
    )


@login_required
def college_feepayment_list(request):
    college_feepayment_list = FeePayment.objects.filter(institute=request.user.institute)
    print(college_feepayment_list)
    # pagination logic
    page = request.GET.get('page')
    revenues_paginated = Paginator(college_feepayment_list, 20)
    if page is None:
        page_college_feepayment_list = revenues_paginated.page(1)
    else:
        page_college_feepayment_list = revenues_paginated.page(page)
    context = {"college_feepayment_list":page_college_feepayment_list}
    return render(request, "tray/college_feepayment_list.html", context)

@login_required
def college_feepayment_details(request,student_id):
    student = Student.objects.get(id=student_id)
    context = {"student":student}
    return render(request, "tray/college_feepayment_details.html",context)


@login_required
def college_alltray_revenue_student_list(request):
    institute = request.user.institute
    students = Student.objects.filter(college=institute)
    # pagination logic
    page = request.GET.get('page')
    students_paginated = Paginator(students, 20)
    if page is None:
        page_students = students_paginated.page(1)
    else:
        page_students = students_paginated.page(page)
    context = {
        "students":page_students,
        "student_page_object": page_students
        }
    return render(request, "tray/college_alltray_revenue_student_list.html", context)

@login_required
def college_alltray_revenue_student_details(request,student_id):
    institute = request.user.institute
    student = get_object_or_404(Student,id=student_id)
    revenues = Revenue.objects.filter(institute=institute,student=student)
    # pagination logic
    page = request.GET.get('page')
    revenues_paginated = Paginator(revenues, 20)
    if page is None:
        page_revenues = revenues_paginated.page(1)
    else:
        page_revenues = revenues_paginated.page(page)

    current_month = datetime.today().strftime("%h")
    month_revenue_total = revenues.aggregate(Sum('day_revenue'))
    try:
        month_revenue_total['day_revenue__sum']
        rounded_month_revenue_total = round(month_revenue_total.get('day_revenue__sum'),2)
    except:
        rounded_month_revenue_total = 0
    context = {"student":student, "revenues":revenues,"page_revenues":page_revenues, "current_month": current_month, "month_revenue_total": rounded_month_revenue_total}
    return render(request, "tray/college_alltray_revenue_student_details.html", context)



@login_required
def college_break_edit(request):
    # institute_id = request.session.get("institute_id")
    # institute = get_object_or_404(Institute,id=institute_id)
    institute = request.user.institute
    try:
        college_break = Break.objects.get(college=institute)
        first_break = college_break.first_break.strftime("%H:%M:%S")
        lunch_break = college_break.lunch_break.strftime("%H:%M:%S")
        last_break = college_break.last_break.strftime("%H:%M:%S")
    except:
        first_break = None
        lunch_break = None
        last_break = None
    context = {"first_break": first_break, "lunch_break":lunch_break, "last_break": last_break}
    return render(request, "tray/college_break_edit.html",context)


@login_required
def college_break_edit_post(request):
    if request.method == "POST":
        first_break = request.POST["first_break"]
        lunch_break = request.POST["lunch_break"]
        last_break = request.POST["last_break"]
        # college_id = request.session["college_id"]
        # college_object = Institute.objects.get(id=college_id)
        college_object = request.user.institute
        break_time_object = Break.objects.get(college=college_object)
        break_time_object.first_break = first_break
        break_time_object.lunch_break = lunch_break
        break_time_object.last_break = last_break
        break_time_object.save()
        return redirect(college_home)


@login_required
def college_recharge(request):
    if request.method == "GET":
        return render(request, "tray/college_recharge.html")
    if request.method == "POST":
        email = request.POST.get("email")
        card = request.POST.get("card_number")
        request.session["college_recharge_student_mail"] = email
        print("card:",card)
        # institute_id = request.session.get("institute_id")
        # institute = Institute.objects.get(id=institute_id)
        institute = request.user.institute
        try:
            if card:
                student_user = Student.objects.get(college=institute, pin_no = card)
                print("student from card", student_user)
                student_name = student_user.name
                student_balance = student_user.balance
            if email:
                user = User.objects.get(email=email)
                student_user = Student.objects.get(user=user)
                student_name = student_user.name
                student_balance = student_user.balance
            request.session["recharge_student_id"] = student_user.id
            return render(
                request,
                "tray/college_recharge_details.html",
                {
                    "student_balance": student_balance,
                    "student_name": student_name,
                },
            )
        except:
            print("_________________finished try block")
            return render(request, 'tray/college_recharge.html', context={'error': 'wrong email or card for student'})
        
@login_required
# this view not in use
def college_recharge_post(request):
    pass

        


@login_required
def college_recharge_details(request):
    return render(request, "tray/college_recharge_details.html")


@login_required
def validate_recharge(request):
    email = request.GET.get("email")
    card = request.GET.get("card")
    college_id = request.session["college_id"]
    if email:
        user_valid = User.objects.filter(email=email).exists()
        if user_valid:
            user = User.objects.get(email=email)
            student_valid = Student.objects.filter(user=user, college=college_id).exists()
        else:
            student_valid = False
    elif card:
        student_valid = Student.objects.filter(college=college_id, pin_no=card).exists()
    print("USER: " + str(student_valid))
    if student_valid:
        if email:
            college_recharge_student_obj = Student.objects.get(
                user=user, college=college_id
            )
        elif card:
            college_recharge_student_obj = Student.objects.get(
                pin_no=card, college=college_id
            )
        college_recharge_student_id = college_recharge_student_obj.id
        request.session["college_recharge_student_id"] = college_recharge_student_id
        print("Student valid: " + str(student_valid) + str(college_id))
        print(str(Institute.objects.get(id=college_id)))
        if student_valid and email:
            data = {"status": "email correct"}
            return JsonResponse(data)
        
        elif student_valid and card:
            data = {"status": "card correct"}
            return JsonResponse(data)

    else:
        print("--------------------entered else")
        if not email:
            data = {"status": "card incorrect"}
            return JsonResponse(data)
        elif not card:
            data = {"status": "email incorrect"}
            return JsonResponse(data)
        if email and card:
            data = {"status": "both email and card incorrect"}
            return JsonResponse(data)

@login_required
def college_recharge_final(request):
    amount = request.GET["amount"]
    recharge_student_id = request.session.get("recharge_student_id")
    student_object = Student.objects.get(id=recharge_student_id)
    current_balance = student_object.balance
    student_object.balance = current_balance + int(amount)
    student_object.save()
    data = {
        "recharge_status": "success",
        "present_balance": student_object.balance,
        "username": student_object.name,
    }
    return JsonResponse(data)


def college_logout(request):
    logout(request)
    return redirect("entry")


# ajaxify with jquery views____________________________________________________________________


@login_required
def validate_store_item(request):
    item_name = request.GET["item_name"]
    data = {"is_taken": Item.objects.filter(item=item_name).exists()}
    return JsonResponse(data)



@login_required
def user_edit_validate(request):
    email = request.GET.get("email")
    present_email = request.user.email
    user_present = User.objects.filter(email=email).exclude(email=present_email).exists()
    data = {"email_taken": user_present}
    return JsonResponse(data)


@login_required
def validate_store_edit_item(request):
    item_name = request.GET["item_name"]
    item_id = request.GET["item_id"]
    data = {
        "is_taken": Item.objects.exclude(id=item_id).filter(item=item_name).exists()
    }
    return JsonResponse(data)


@login_required
def add_new_store_item(request):
    return


@login_required
def update_store_status(request):
    store_open = request.GET["open"]
    store_id = request.GET["store_id"]
    store = Store.objects.get(id=store_id)

    if store_open == "Closed":
        store.store_status = False
        store.save()
        data = {"is_open": "false"}
        return JsonResponse(data)

    elif store_open == "Open":
        store.store_status = True
        store.save()
        data = {"is_open": "true"}

        return JsonResponse(data)


@login_required
def update_item_availability(request):
    if request.GET["status"] == "availability_change":
        availability = request.GET["availability"]
        item_id = request.GET["item_id"]
        store_id = request.GET["store_id"]
        store = Store.objects.get(id=store_id)
        item = Item.objects.get(id=item_id, store=store)
        if availability == "available":
            item.available = True
            item.save()
            data = {"available": "true"}
            return JsonResponse(data)

        elif availability == "unavailable":
            item.available = False
            item.save()
            data = {"available": "false"}
            return JsonResponse(data)

    if request.GET["status"] == "delete_item":
        item_id = request.GET["item_id"]
        store_id = request.GET["store_id"]
        store = Store.objects.get(id=store_id)
        if Item.objects.filter(id=item_id, store=store).exists():
            item = Item.objects.get(id=item_id, store=store)
            item.delete()
            data = {"deleted": "true"}
            return JsonResponse(data)

        else:
            data = {"deleted": "false"}
            return JsonResponse(data)


def validate_entry(request):
    username = request.GET["email"]
    password = request.GET["password"]
    user_exist = User.objects.filter(email=username).exists()
    if user_exist:
        user_student_exist = User.objects.filter(email=username).exists()
    else:
        user_student_exist = False

    if user_student_exist:
        user = User.objects.get(email=username)
        password_checker_bool = check_password(password, user.password)
        if password_checker_bool == False:
            data = {
                "incorrect_status": "incorrect_password",
            }
        else:
            data = {
                "incorrect_status": "correct",
            }
        return JsonResponse(data)
    else:
        data = {"incorrect_status": "wrong_email"}
        return JsonResponse(data)


@login_required
def validate_order_cancel(request):
    order_id = request.GET["order_id"]
    order = Order.objects.get(id=order_id)
    item_name = order.item
    #'break_time_find' is variable which gives break name in string format from the respective order. eg. 'First Break'
    break_time_find = order.pickup_time
    # this isn't hard code 'id = 1' there is only one break object for now will change and add relation
    break_object = Break.objects.get(college=order.student.college)
    if break_time_find == "First Break":
        break_time = break_object.first_break
    elif break_time_find == "Lunch Break":
        break_time = break_object.lunch_break
    elif break_time_find == "Last Break":
        break_time = break_object.last_break
    else:
        break_time = "Now"
    if order.status == True:
        data = {"cancelled": "already_delivered"}
        return JsonResponse(data)

    if break_time == "Now":
        student_balance = order.student.balance
        store_balance = order.store.store_balance
        student_balance = order.student.balance + order.cost
        order.student.balance = student_balance
        store_balance = order.store.store_balance - order.cost
        order.store.store_balance = store_balance
        order.student.save()
        order.store.save()
        order.delete()
        data = {"cancelled": "success", "item": item_name}
        return JsonResponse(data)
    else:
        #'break_time' contains the break time selected for the order
        #'cancel_time' is time when order is requested to be cancelled
        cancel_time = datetime.now()
        time_difference = break_time.hour - cancel_time.hour
        if time_difference >= 0:
            student_balance = order.student.balance
            student_balance = order.student.balance + order.cost
            order.student.balance = student_balance
            order.student.save()
            order.delete()

            data = {"cancelled": "success"}
            return JsonResponse(data)

        elif time_difference < 1:
            data = {"cancelled": "failure"}
            return JsonResponse(data)


@login_required
def cart(request):
    # block that adds items to cart
    student = False
    store = False
    if request.GET["status"] == "add_to_cart":
        # can cache student and store object
        # no need to query them on each add_to_cart
        if student == False and store == False:
            student_id = request.GET["student_id"]
            student = Student.objects.get(id=student_id)
            store_id = request.GET["store_id"]
            store = Store.objects.get(id=store_id)
        item_name = request.GET["item_name"]
        # time = request.GET['time']
        quantity = request.GET["quantity"]

        if Item.objects.filter(item=item_name).exists():
            item = Item.objects.get(item=item_name)
            price = item.price
            # cost = int(price) * int(quantity)
            # cart_item = CartItem(item = item_name, quantity = quantity, cost = cost, pickup_time = time, store = store, student = student )
            # cart_item.save()
            # item.save()
            data = {
                "added": "success",
                "item_price": price,
            }
            return JsonResponse(data)
        else:
            data = {"added": "failure"}
            return JsonResponse(data)

    if request.GET["status"] == "leaving_page":
        data = {"status": "cart_count_reset"}
        return JsonResponse(data)

    if request.GET["status"] == "confirm_order":
        print("reached confirm")
        time = request.GET["time"]
        store_id = request.GET["store_id"]
        store = Store.objects.get(id=store_id)
        institute = store.college
        student_id = request.GET["student_id"]
        total = request.GET["total"]
        # revenue = request.GET["revenue"]
        student = Student.objects.get(id=student_id)
        print(student)
        # cart_items = CartItem.objects.filter(student = student)
        if int(student.balance) > int(total):
            # generating otp for the cart of items
            # generating random strings
            # using random.choices()
            # initializing size of string
            N = 4
            # using random.choices()
            # generating random strings
            res = "".join(random.choices(string.ascii_lowercase, k=N))
            otp = str(res)
            # taking orders as json
            load = json.loads(request.GET["order_list_json"])
            # passing json load to bulk create on orders db
            # creating orders on db
            objects = []
            new_object = []
            purchase_id = purchase_id_generator(store)
            # creating order group
            order_group = OrderGroup(store = store, student = student, otp = otp, order_group_total=0)
            for i in load:
                order_group.order_group_total += (i["price"]*i["quantity"])
                new_object = Order(
                    item=i["item"],
                    cost=i["price"]*i["quantity"],
                    quantity=i["quantity"],
                    pickup_time=time,
                    otp=otp,
                    store=store,
                    student=student,
                    purchase_id=purchase_id,
                    order_group=order_group,
                )
                order_group.save()
                objects.append(new_object)
                item = Item.objects.get(item=i["item"])
                # initializing stock of item variable
                item_stock = item.stock
                # updating stock at store
                item.stock = int(item_stock) - int(i["quantity"])
                item.save()
                # unticking item availability to customers on reaching low stock at store
                if item.stock < 5:
                    item.available = False
                    item.save()
                # updating store balance
                cost = i["quantity"] * i["price"]
                store.store_balance = store.store_balance + cost
                store.save()
                # updating student balance
                student.balance = student.balance - (cost + (order_group.order_group_total * 0.01) )
                student.save()
            # setting and checking the free trial period
            free_trial_expiry_date = institute.created_at.date() + relativedelta(months=2)
            if date.today() < free_trial_expiry_date:
                # conditional block to calculate revenue after free trial
                try:
                    revenue = Revenue.objects.get(created_at__date=date.today(), student = student, institute=institute)
                    revenue.total = revenue.total + order_group.order_group_total
                    revenue.day_revenue = revenue.total * 0.01
                    revenue.save()
                    print("incrementing revenue", revenue.day_revenue)
                except:
                    day_order_groups_total = OrderGroup.objects.filter(created_at__date=date.today(),student=student).aggregate(Sum('order_group_total'))
                    print("initial revenue total",day_order_groups_total)
                    revenue = Revenue.objects.create(total=int(day_order_groups_total["order_group_total__sum"]), day_revenue= float(day_order_groups_total["order_group_total__sum"] *0.01), student = student)
                    print("creating revenue value of the day", revenue.day_revenue)
            # saving orders to db
            Order.objects.bulk_create(objects)

            data = {
                "status": "order_placed",
                "cart_items": False,
                "total": total,
                "otp": otp,
            }
            return JsonResponse(data)

        elif int(student.balance) < int(total):
            data = {"status": "low_balance"}
            return JsonResponse(data)

    if request.GET["status"] == "delete_from_cart":
        item_id = request.GET["item_id"]
        # cart_item = CartItem.objects.get(id=item_id)
        # cart_item.delete()
        data = {"status": "item_deleted"}
        return JsonResponse(data)


def purchase_id_generator(store):
    last_bill = Order.objects.filter(store=store).order_by("id").last()
    if last_bill:
        purchase_id = last_bill.purchase_id
    else:
        purchase_id = 0000
    new_purchase_id = purchase_id + 1
    return new_purchase_id


def paytm(request):
    return render(request, "paytm_checkout.html")


@login_required
def pickup_order(request):
    order_id = request.GET["order_id"]
    order = Order.objects.get(id=order_id)
    order.status = True
    order.save()
    data = {"deliver": "true"}
    return JsonResponse(data)


def store_login_validate(request):
    email = request.GET["email"]
    password = request.GET["password"]
    user_exists = User.objects.filter(email=email).exists()
    if user_exists:
        user = User.objects.get(email=email)
        user_store_exist = Store.objects.filter(user=user).exists()
    else:
        user_store_exist = False

    if user_store_exist:
        password_check = check_password(password, user.password)
        if password_check:
            data = {"validity": "correct"}
            return JsonResponse(data)
        else:
            data = {"validity": "wrong_password"}
            return JsonResponse(data)
    else:
        data = {"validity": "invalid_user"}
        return JsonResponse(data)


def college_login_validate(request):
    user_name = request.GET["user_name"]
    password = request.GET["password"]
    user_exists = User.objects.filter(username=user_name).exists()
    if user_exists:
        user = User.objects.get(username=user_name)
        user_institute_exist = Institute.objects.filter(user=user).exists()
    else:
        user_institute_exist = False

    if user_institute_exist:
        password_check = check_password(password, user.password)
        if password_check:
            data = {"validity": "correct"}
            return JsonResponse(data)
        else:
            data = {"validity": "wrong_password"}
            return JsonResponse(data)
    else:
        data = {"validity": "invalid_user"}
        return JsonResponse(data)


def store_register_validate(request):
    store_name = request.GET["store_name"]
    college_id = request.GET["college_id"]
    email = request.GET["email"]
    college_object = Institute.objects.get(id=college_id)
    data = {
        "store_name_taken": Store.objects.filter(
            store_name=store_name, college=college_object
        ).exists(),
        "email_taken": User.objects.filter(email=email).exists(),
    }
    return JsonResponse(data)


@login_required
def store_edit_validate(request):
    store_name = request.GET["store_name"]
    college_id = request.GET["college_id"]
    store_id = request.GET["store_id"]
    college_object = Institute.objects.get(id=college_id)
    data = {
        "store_name_taken": Store.objects.exclude(id=store_id)
        .filter(store_name=store_name, college=college_object)
        .exists()
    }
    return JsonResponse(data)


def college_register_validate(request):
    college_name = request.GET["college_name"]
    email = request.GET["email"]
    data = {
        "college_name_taken": Institute.objects.filter(
            institute_name=college_name
        ).exists(),
        "email_taken": User.objects.filter(email=email).exists(),
    }
    print("email taken" + str(data["email_taken"]))
    return JsonResponse(data)


def student_register_validate(request):
    email = request.GET["email"]
    password = request.GET["password"]
    card_pin = request.GET["card_pin"]
    card_pin_taken = False
    if card_pin:
        card_pin_taken = Student.objects.filter(pin_no=card_pin).exists()
    data = {
        "email_taken": User.objects.filter(email=email).exists(),
        "card_pin_taken": card_pin_taken,
    }
    print("email_taken" + str(data["email_taken"]))
    return JsonResponse(data)


@login_required
def student_pin_edit_validate(request):
    password = request.GET["password"]
    student_id = request.GET["student_id"]
    pin_no_hash = make_password(pin_no, "pepper")
    data = {
        "pin_taken": Student.objects.exclude(id=student_id)
        .filter(pin_no=pin_no)
        .exists(),
    }
    return JsonResponse(data)


@login_required
def bulk_recharge_submit(request):
    mails = json.loads(request.GET["mails"])
    recharge_amount = request.GET["recharge_amount"]
    # college_id = request.session["college_id"]
    # college = Institute.objects.get(id=college_id)
    college = request.user.institute
    print(mails)
    print("amount: " + recharge_amount)
    new_mail = []
    all_mail_objects = []
    for i in mails:
        new_mail = BulkRechargeMail.objects.create(
            email=i, recharge_amount=recharge_amount, college=college
        )
        all_mail_objects.append(new_mail)
    # removed bulk create as the id is not available for each created object and thus update of fields creates duplicate objects
    # bulk_recharge_mails = BulkRechargeMail.objects.bulk_create(all_mail_objects)
    # print(type(bulk_recharge_mails))
    # print(bulk_recharge_mails)
    college_students = Student.objects.filter(college=college)

    for recharge_mail in all_mail_objects:
        for student in college_students:
            if student.user.email == recharge_mail.email:
                student.balance = int(student.balance) +  int(recharge_mail.recharge_amount)
                # shows student account is charged
                print("id-----",recharge_mail.id)
                print("entered if")
                recharge_mail.active = True
                # shows student account already present
                recharge_mail.account_status = True
                recharge_mail.student = student
                recharge_mail.save()
                student.save()
        
    data = {"added": "success"}
    return JsonResponse(data)


@login_required
def home_store_status_update(request):
    store_id = request.GET["store_id"]
    store = Store.objects.get(id=store_id)
    if store.store_status:
        data = {"store_status": "open"}
        return JsonResponse(data)
    else:
        data = {"store_status": "closed"}
        return JsonResponse(data)


def institute_kiosk(request,institute_name):
    try:
        institute = Institute.objects.get(institute_name=institute_name)
    except:
        context = {
            "error":"Incorrect institute name in url"
        }
        return render(request, "tray/institute_kiosk.html",context)
    events = InstituteEvent.objects.filter(institute=institute )
    upcoming_events = InstituteEvent.objects.exclude( created_at__date=date.today()).filter(institute=institute)
    today_events = InstituteEvent.objects.filter(institute=institute, created_at__date=date.today())
    context = {
        "institute":institute,
        "today_events":today_events,
        "upcoming_events":upcoming_events,
    }
    return render(request, "tray/institute_kiosk.html",context)