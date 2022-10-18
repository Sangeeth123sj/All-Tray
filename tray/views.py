# from django.contrib.auth.models import User
from django.contrib.auth import authenticate, get_user_model, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render


from .models import (
    Bill,
    Break,
    BulkRechargeMail,
    CartItem,
    Institute,
    Item,
    Order,
    Store,
    Student,
    User,
)

User = get_user_model()
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


def register_card(request):
    colleges = Institute.objects.all()
    return render(request, "tray/register_card.html", {"colleges": colleges})


def register_card_post(request):
    if request.method == "POST":
        student_name = request.POST["student_name"]
        branch = request.POST["branch_name"]
        semester = request.POST["semester"]
        password = request.POST["password"]
        card_pin = request.POST["card_pin"]
        college_id = request.POST["college_id"]
        email = request.POST["mail_id"]
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
            bulk_recharge_email = BulkRechargeMail.objects.get(email=email)
            student.balance = bulk_recharge_email.recharge_amount
            student.save()
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


def home_post(request):
    if request.method == "POST":
        email = request.POST["email"]
        password = request.POST["password"]
        request.session["email"] = email
        request.session["password"] = password
        user = authenticate(request, email=email, password=password)
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
def your_orders_post(request):
    if request.method == "POST":
        student_id = request.POST["student_id"]
        request.session["student_id"] = student_id
        return redirect(your_orders)


@login_required
def your_orders(request):
    student_id = request.session["student_id"]
    student_object = Student.objects.get(id=student_id)
    orders = Order.objects.filter(student=student_object)
    order_exist = Order.objects.filter(student=student_object).exists()
    if order_exist:
        otp = orders.first().otp
    else:
        otp = ""
    return render(request, "tray/your_orders.html", {"orders": orders, "otp": otp})


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
    student_id = request.session["student_id"]
    store_id = request.session["store_id"]
    student = Student.objects.get(id=student_id)
    college = student.college
    store = Store.objects.get(id=store_id)
    items = store.item_set.filter(available=True)
    return render(
        request,
        "tray/order_page.html",
        {"student": student, "store": store, "college": college, "items": items},
    )


@login_required
def student_pin_edit(request):
    student_id = request.session["student_id"]
    student = Student.objects.get(id=student_id)
    request.session["student_id"] = student_id
    return render(request, "tray/student_pin_edit.html", {"student": student})


@login_required
def student_pin_edit_post(request):
    student_id = request.session["student_id"]
    if request.method == "POST":
        print(student_id)
        password = request.POST["password"]
        student = Student.objects.get(id=student_id)
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
def store_home(request):
    store_id = request.session["store_id"]
    store = Store.objects.get(id=store_id)
    store_name = store.store_name
    items = store.item_set.all()
    status = store.store_status
    request.session["store_id"] = store_id
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
            "store_id": store_id,
            "status": c,
            "items": items,
        },
    )


@login_required
def store_billing(request):
    store_id = request.session["store_id"]
    print("entering billing store id  = " + str(store_id))
    store = Store.objects.get(id=store_id)
    store_name = store.store_name
    items = store.item_set.all()
    context = {"store": store, "store_name": store_name, "items": items}
    return render(request, "tray/store_billing.html", context)


@login_required
def billing_item_price(request):
    item_name = request.GET["item_name"]
    store_id = request.GET["store_id"]
    # store = Store.objects.get(id = store_id)
    item = Item.objects.get(item=item_name, store=store_id)
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
    store_id = request.session["store_id"]
    store = Store.objects.get(id=store_id)
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
            data = {"card_status": "card_invalid"}
            return JsonResponse(data)
        elif student_check:
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
    for i in load:
        new_object = Bill(
            item=i["item"],
            price=i["price"],
            quantity=i["quantity"],
            invoice_no=new_invoice_no,
            invoice=file,
            store=store,
        )
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
            pin_no = request.GET["pin_no"]
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

    data = {}
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
    store_id = request.session["store_id"]
    store_object = Store.objects.get(id=store_id)
    college_object = store_object.college
    return render(
        request,
        "tray/store_edit_details.html",
        {"store": store_object, "college": college_object},
    )


@login_required
def store_edit_details_post(request):
    if request.method == "POST":
        store_id = request.session["store_id"]
        store_name = request.POST["store_name"]
        store_details = request.POST["store_description"]
        store_object = Store.objects.get(id=store_id)
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
        store_id = request.session["store_id"]
        item_name = request.POST["item_name"]
        stock = request.POST["stock"]
        price = request.POST["price"]
        store_object = Store.objects.get(id=store_id)
        new_item = Item(item=item_name, stock=stock, price=price, store=store_object)
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
    store_id = request.session["store_id"]
    store_object = Store.objects.get(id=store_id)
    orders = Order.objects.filter(store=store_object)
    sorted_orders = orders.order_by("student", "pickup_time")
    current_month = datetime.today().strftime("%h")
    current_month_number = datetime.today().month
    # month_total = orders.filter(created_at__month = current_month_number ).aggregate(Sum('cost'))
    month_orders = orders.filter(created_at__month=current_month_number)
    month_total = 0
    for order in month_orders:
        total = order.cost * order.quantity
        month_total = month_total + total
    return render(
        request,
        "tray/store_order_list.html",
        {
            "orders": sorted_orders,
            "current_month": current_month,
            "month_total": month_total,
        },
    )


@login_required
def store_item_pickup(request):
    store_id = request.session["store_id"]
    request.session["store_id"] = store_id
    return render(request, "tray/store_item_pickup.html")


@login_required
def store_item_pickup_validate(request):
    otp_or_card = request.GET["otp_or_card"]
    print("otp or card: " + str(type(otp_or_card)))
    check_otp = Order.objects.filter(
        otp=otp_or_card, created_at__date=date.today()
    ).exists()
    print("check otp " + str(check_otp))
    if check_otp:
        request.session["otp_or_card_selected"] = "otp"
        data = {
            "incorrect_status": "correct_otp",
        }
        return JsonResponse(data)
    else:
        check_student_valid = Student.objects.filter(pin_no=otp_or_card).exists()
        print("check student: " + str(check_student_valid))
        if check_student_valid:
            check_student = Student.objects.get(pin_no=otp_or_card)
            check_card = Order.objects.filter(
                student=check_student, created_at__date=date.today()
            ).exists()
            # order = Order.objects.filter( created_at__date = date.today(), student = student)

        else:
            check_card = False
    if check_card:
        request.session["otp_or_card_selected"] = "card"
        data = {"card_pin": "correct_card_pin"}
        return JsonResponse(data)
    else:
        data = {
            "incorrect_status": "incorrect_otp_and_card",
        }
        return JsonResponse(data)


@login_required
def user_pickup_orders_post(request):
    if request.method == "POST":
        otp_or_card = request.POST["otp_or_card"]
        request.session["otp_or_card"] = otp_or_card
        return redirect(user_pickup_orders)


@login_required
def user_pickup_orders(request):
    store_id = request.session["store_id"]
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
    store_id = request.session["store_id"]
    store_object = Store.objects.get(id=store_id)
    store_bills = Bill.objects.filter(store=store_object)
    # sorted_orders = orders.order_by('student', 'pickup_time')
    return render(
        request,
        "tray/store_bills.html",
        {"store": store_object, "store_bills": store_bills},
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
        user = User.objects.create_user(email, password)
        user.save()
        institute = Institute(
            institute_name=college,
            user=user,
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
    institute_id = request.session["institute_id"]
    college = Institute.objects.get(id=institute_id)
    request.session["college_id"] = college.id
    stores = Store.objects.filter(college=college)

    return render(
        request, "tray/college_home.html", {"college": college, "stores": stores}
    )


@login_required
def college_bulk_recharge(request):
    return render(request, "tray/college_bulk_recharge.html")


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
    sorted_orders = orders.order_by("student", "pickup_time")
    current_month = datetime.today().strftime("%h")
    current_month_number = datetime.today().month
    # month_total = orders.filter(created_at__month = current_month_number ).aggregate(Sum('cost'))
    month_orders = orders.filter(created_at__month=current_month_number)
    month_total = 0
    for order in month_orders:
        total = order.cost * order.quantity
        month_total = month_total + total
    return render(
        request,
        "tray/college_store_order_list.html",
        {
            "orders": sorted_orders,
            "store": store_object,
            "current_month": current_month,
            "month_total": month_total,
        },
    )


@login_required
def college_break_edit(request):
    return render(request, "tray/college_break_edit.html")


@login_required
def college_break_edit_post(request):
    if request.method == "POST":
        first_break = request.POST["first_break"]
        lunch_break = request.POST["lunch_break"]
        last_break = request.POST["last_break"]
        college_id = request.session["college_id"]
        college_object = Institute.objects.get(id=college_id)
        break_time_object = Break.objects.get(college=college_object)
        break_time_object.first_break = first_break
        break_time_object.lunch_break = lunch_break
        break_time_object.last_break = last_break
        break_time_object.save()
        return redirect(college_home)


@login_required
def college_recharge(request):
    return render(request, "tray/college_recharge.html")


@login_required
def college_recharge_post(request):
    if request.method == "POST":
        email = request.POST["email"]
        college_recharge_student_id = request.session["college_recharge_student_id"]
        student_object = Student.objects.get(id=college_recharge_student_id)
        student_name = student_object.name
        student_balance = student_object.balance
    return render(
        request,
        "tray/college_recharge_details.html",
        {
            "email": email,
            "student_balance": student_balance,
            "student_name": student_name,
        },
    )


@login_required
def college_recharge_details(request):
    return render(request, "tray/college_recharge_details.html")


@login_required
def validate_recharge(request):
    email = request.GET["email"]
    print(email)
    college_id = request.session["college_id"]
    user_valid = User.objects.filter(email=email).exists()
    print("USER: " + str(user_valid))
    if user_valid:
        user = User.objects.get(email=email)
        student_valid = Student.objects.filter(user=user, college=college_id).exists()
        college_recharge_student_obj = Student.objects.get(
            user=user, college=college_id
        )
        college_recharge_student_id = college_recharge_student_obj.id
        request.session["college_recharge_student_id"] = college_recharge_student_id
        print("Student valid: " + str(student_valid) + str(user) + str(college_id))
        print(str(Institute.objects.get(id=college_id)))
        if student_valid:
            data = {"email_status": "correct"}
            return JsonResponse(data)
        else:
            data = {"email_status": "incorrect"}
            return JsonResponse(data)

    else:
        data = {"email_status": "incorrect"}
        return JsonResponse(data)


@login_required
def college_recharge_final(request):
    email = request.GET["email"]
    amount = request.GET["amount"]
    user = User.objects.get(email=email)
    student_object = Student.objects.get(user=user)
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
                #'time' : time,
            }
            return JsonResponse(data)
        else:
            data = {"added": "failure"}
            return JsonResponse(data)

    if request.GET["status"] == "leaving_page":
        data = {"status": "cart_count_reset"}
        return JsonResponse(data)

    if request.GET["status"] == "confirm_order":
        time = request.GET["time"]
        store_id = request.GET["store_id"]
        store = Store.objects.get(id=store_id)
        student_id = request.GET["student_id"]
        total = request.GET["total"]
        revenue = request.GET["revenue"]
        student = Student.objects.get(id=student_id)
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
            # creating bill orders on db
            objects = []
            new_object = []
            purchase_id = purchase_id_generator(store)
            for i in load:
                new_object = Order(
                    item=i["item"],
                    cost=i["price"],
                    quantity=i["quantity"],
                    pickup_time=time,
                    otp=otp,
                    store=store,
                    student=student,
                    revenue=revenue,
                    purchase_id=purchase_id,
                )
                # new_object = Bill(item=i['item'], price=i['price'], quantity=i['quantity'], invoice_no=new_invoice_no,invoice=file , store=store)
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
                student.balance = student.balance - cost
                student.save()
            # saving orders to db
            Order.objects.bulk_create(objects)

            # for cart_item in cart_items :
            #    item = Item.objects.get(item = cart_item.item)
            #    #initializing stock of item variable
            #    item_stock = item.stock
            #    #saving the order from cart
            #    order = Order(item = cart_item.item, quantity = cart_item.quantity, cost = cart_item.cost, pickup_time = cart_item.pickup_time, otp=otp, store = cart_item.store, student = cart_item.student )
            #    order.save()
            # updating stock at store
            #    item.stock = int(item_stock) - int(cart_item.quantity)
            # unticking item availability to customers on reaching low stock at store
            #    if item.stock < 5:
            #        item.available = False
            #    item.save()
            # updating store balance
            # store.store_balance = store.store_balance + int(cart_item.cost)
            # store.save()
            # updating student balance
            # student.balance = student.balance - int(cart_item.cost)
            # student.save()
            # deleting item from cart
            # cart_item.delete()

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
        cart_item = CartItem.objects.get(id=item_id)
        cart_item.delete()
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
    college_id = request.session["college_id"]
    college = Institute.objects.get(id=college_id)
    print(mails)
    print("amount: " + recharge_amount)
    new_mail = []
    all_mail_objects = []
    for i in mails:
        new_mail = BulkRechargeMail(
            email=i, recharge_amount=recharge_amount, college=college
        )
        all_mail_objects.append(new_mail)
    BulkRechargeMail.objects.bulk_create(all_mail_objects)
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
