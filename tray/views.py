from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import Student,Item,Store,User,Order, Break, CartItem, Institute, Bill
from django.db.models import Sum
from django.contrib.auth.models import User, Permission
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.http import JsonResponse
from datetime import datetime
from datetime import timedelta
from django.contrib.auth.hashers import check_password, make_password
import string,random
import requests
import json
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from .modules.invoice import *
from django.http import FileResponse
from django.core.files.base import  File

# import checksum generation utility
# You can get this utility from https://developer.paytm.com/docs/checksum/
import paytmchecksum





#student views______________________________________________________________________________

def register_card(request):
    colleges = Institute.objects.all()
    return render(request, 'tray/register_card.html', {'colleges': colleges})

def register_card_post(request):
    if request.method == 'POST':
        student_name = request.POST['student_name']
        branch = request.POST['branch_name']
        semester = request.POST['semester']
        password = request.POST['password']
        college_id = request.POST['college_id']
        email = request.POST['mail_id']
        college_object = Institute.objects.get(id = college_id)
        user = User.objects.create_user(student_name,email,password)
        user.save
        student = Student(name = student_name, branch = branch, sem = semester,college = college_object, user = user)
        student.save()
        messages.success(request, 'Profile created.')
        return render (request, 'tray/entry.html')

def entry(request):
    if request.user.is_authenticated:
        student_user = Student.objects.filter(user = request.user).exists()
        store_user = Store.objects.filter(user = request.user).exists()
        college_user = Institute.objects.filter(user = request.user).exists()
        if student_user:
            print("Already logged in student")
            return redirect('home')
        if store_user:
            print("Already logged in store")
            return redirect('store_home')
        if college_user:
            print("Already logged in college")
            return redirect('college_home')
        else:
            return render (request, 'tray/entry.html')
    else:
        return render (request, 'tray/entry.html')

def home_post(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        request.session['username'] = username
        request.session['password'] = password
        return redirect(home)

def home(request):
    student_username = request.session['username']
    student_password = request.session['password']
    user = authenticate(request, username = student_username, password = student_password)
    print("Student "+str(user)+" just logged in")
    
    if user is not None:
        login(request, user)
        stores = Store.objects.filter(college = user.student.college)
        student = user.student
        request.session['student_id'] = student.id
        return render (request, 'tray/home.html', {'stores':stores, 'student': student})
    else:
        c = "Sorry login failed!"
        return HttpResponse(c)  


def your_orders_post(request):
    if request.method == 'POST':
        student_id = request.POST['student_id']
        request.session['student_id'] = student_id
        return redirect(your_orders)

def your_orders(request):
        student_id = request.session['student_id']
        student_object = Student.objects.get(id = student_id)
        orders = Order.objects.filter(student = student_object)
        order_exist = Order.objects.filter(student = student_object).exists()
        if order_exist:
            otp = orders.first().otp
        else:
            otp = ""
        return render(request, 'tray/your_orders.html', {'orders': orders, 'otp': otp})

def order_page_post(request):
    if request.method == 'POST':
        student_id = request.POST['student_id']
        store_id = request.POST['store_id']
        request.session['student_id'] = student_id
        request.session['store_id'] = store_id
        return redirect (order_page)
    else:
        c = "Sorry login failed!"
        return HttpResponse(c)   

def order_page(request):
    student_id = request.session['student_id']
    store_id = request.session['store_id']
    student = Student.objects.get(id = student_id)
    store = Store.objects.get(id = store_id)
    items = store.item_set.filter(available = True)
    return render (request, 'tray/order_page.html', {'student': student, 'store': store, 'items': items})

def student_pin_edit(request):
    student_id = request.session['student_id']
    student = Student.objects.get(id = student_id)
    request.session['student_id'] = student_id
    return render(request, 'tray/student_pin_edit.html', {'student': student})

def student_pin_edit_post(request):
    student_id = request.session['student_id']
    if request.method == 'POST':
        print(student_id)
        password = request.POST['password']
        student = Student.objects.get(id = student_id)
        u = student.user
        u.set_password(password)
        u.save()
        logout(request)
        return redirect(entry)


def student_logout(request):
    logout(request)
    return redirect('entry')

#store views_______________________________________________________________________________

def open_store(request):
    colleges = Institute.objects.all()
    return render(request, 'tray/open_store.html', {'colleges':colleges} )

def open_store_success(request):
    if request.method == 'POST':
        college_id = request.POST['college_id']
        institute = Institute.objects.get(id = college_id)
        username = request.POST['username']
        store_name = request.POST['store_name']
        store_details = request.POST['store_description']
        email = request.POST['email']
        password = request.POST['password']
        user = User.objects.create_user(username,email,password)
        user.save
        store = Store( store_name = store_name, store_status=True, store_details=store_details, college = institute, user = user )
        store.save()
        return redirect(store_login)

def store_login(request):
    if request.user.is_authenticated:
        store_user = Store.objects.filter(user = request.user).exists()
        if store_user:
            print("Already logged in store")
            return redirect('store_home')
        else:
            return render (request, 'tray/login_store.html')
    else:
        return render(request, 'tray/login_store.html' )


def store_login_processing(request):
    username = request.POST['username']
    password = request.POST['password']
    user = authenticate(request, username = username, password = password)

    if user is not None:
        logout(request)
        login(request, user)
        store_id = user.store.id
        request.session['store_id'] = store_id
        return redirect('store_home')
    else:
        c = "Sorry login failed!"
        return HttpResponse(c)   

def store_home(request):
    store_id = request.session['store_id']
    store = Store.objects.get(id = store_id)
    store_name = store.store_name
    items = store.item_set.all()
    status = store.store_status
    request.session['store_id'] = store_id
    if status == True:
        c = "Open"
    else:
        c = "Closed"
    return render(request, 'tray/store_home.html',{'store': store, 'store_name':store_name, 'store_id':store_id, 'status':c, 'items':items})

def store_billing(request):
    store_id = request.session['store_id']
    print("entering billing store id  = "+str(store_id))
    store = Store.objects.get(id = store_id)
    store_name = store.store_name
    items = store.item_set.all()
    context = {'store':store,'store_name':store_name, 'items': items}
    return render (request, 'tray/store_billing.html', context )

def billing_item_price(request):
    item_name = request.GET['item_name']
    store_id = request.GET['store_id']
    #store = Store.objects.get(id = store_id)
    item = Item.objects.get(item = item_name, store = store_id)
    item_price = item.price
    data = {
        'item_price' : item_price,
    }
    return JsonResponse(data)

def invoice_number_gen(store):
    last_bill = Bill.objects.all().order_by('id').last()
    if last_bill:
        last_invoice_no = last_bill.invoice_no
        #invoice number format is 'customer_name_short + number' eg: CS003 
        last_invoice_initials = last_invoice_no[:2]    
        last_invoice_digits =  last_invoice_no[2:]     
        new_invoice_digits = int(last_invoice_digits) + 1
        new_invoice_no =  last_invoice_initials+ str(new_invoice_digits)
    else:
        new_invoice_no = store.invoice_code + str(1)
    return (new_invoice_no) 

def billing_invoice(request):
    store_id = request.session['store_id']
    store = Store.objects.get(id = store_id)
    store_name = store.store_name
    load = json.loads(request.GET['order_list_json'])
    total = request.GET['total']
    device = request.GET['device']
    request.session['device'] = device
    #generating incremented invoice no
    new_invoice_no = invoice_number_gen(store)
    
    #load is the list of orders
    #creating innvoice pdf
    create_invoice( store_name, new_invoice_no, load, total)
    #preparing invoice file for Bill db
    f = open('media/pdf/'+new_invoice_no, 'rb')
    file = File(f)
    #creating bill orders on db
    objects = []
    new_object = []
    #assigning invoice number and other details
    for i in load:
        new_object = Bill(item=i['item'], price=i['price'], quantity=i['quantity'], invoice_no=new_invoice_no,invoice=file , store=store)
        objects.append(new_object)
    Bill.objects.bulk_create(objects)
    
    print(store_name)
    #print(load[0]["item"])
    request.session['invoice_name'] =  new_invoice_no
    
    data={
        
    }
    return JsonResponse(data)

def invoice_print(response):
    device = response.session['device']
    invoice_name = response.session['invoice_name']
    pdf = open('media/pdf/'+invoice_name, 'rb')
    #device specific print or download
    if device == 'desktop':
        response = FileResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = 'inline'
        
    elif device == 'mobile':
        response = FileResponse(pdf)
        response['Content-Disposition'] = 'attachment; filename= "' + invoice_name + '"'
    return response

def store_edit_details(request):
    store_id = request.session['store_id']
    store_object = Store.objects.get(id = store_id)
    college_object = store_object.college
    return render(request, 'tray/store_edit_details.html',{'store': store_object, 'college': college_object })

def store_edit_details_post(request):
    if request.method == 'POST':
        store_id = request.session['store_id']
        store_name = request.POST['store_name']
        store_details = request.POST['store_description']
        store_object = Store.objects.get(id = store_id)
        store_object.store_name = store_name
        store_object.store_details = store_details
        store_object.save()
    return redirect(store_home)

def store_add_item(request):
    store_id = request.session['store_id']
    return render (request, 'tray/store_add_item.html',{'store_id': store_id})
    

def store_add_item_save(request):
    if request.method == 'POST':
        store_id = request.session['store_id']
        item_name = request.POST['item_name']
        stock = request.POST['stock']
        price = request.POST['price']
        store_object = Store.objects.get(id = store_id)
        new_item = Item(item = item_name, stock = stock, price = price, store = store_object)
        new_item.save()
    return redirect(store_home)

def edit_items_post(request):
    if request.method == 'POST':
       item_id = request.POST['item_id']
       store_id = request.POST['store_id']
       request.session['store_id'] = store_id
       request.session['item_id'] = item_id
       return redirect (edit_items)

def edit_items(request):
    store_id = request.session['store_id']
    item_id = request.session['item_id']
    item = Item.objects.get(id = item_id)
    return render(request, 'tray/edit_store_items.html', {'item': item, 'store_id': store_id} )

def edit_item_save(request):
    if request.method == 'POST':
        item_id = request.POST['item_id']
        edited_item_name = request.POST['item_name']
        edited_stock = request.POST['stock']
        edited_price = request.POST['price']
        edited_item = Item.objects.get(id = item_id )
        edited_item.item =  edited_item_name
        edited_item.stock =  edited_stock
        edited_item.price =  edited_price
        edited_item.save()
    return redirect(store_home)

def store_logout(request):
    logout(request)
    return redirect('store_login')

def store_order_list(request):
    store_id = request.session['store_id']
    store_object = Store.objects.get(id = store_id)
    orders = Order.objects.filter(store = store_object)
    sorted_orders = orders.order_by('student', 'pickup_time')
    current_month = datetime.today().strftime("%h")
    current_month_number = datetime.today().month
    #month_total = orders.filter(created_at__month = current_month_number ).aggregate(Sum('cost'))
    month_orders = orders.filter(created_at__month = current_month_number )
    month_total = 0
    for order in month_orders:
        total = order.cost * order.quantity
        month_total = month_total + total 
    return render(request, 'tray/store_order_list.html',{'orders': sorted_orders, 'current_month': current_month, 'month_total': month_total}) 

def store_item_pickup(request):
    store_id = request.session['store_id']
    request.session['store_id'] = store_id 
    return render(request, 'tray/store_item_pickup.html')


def store_item_pickup_validate(request):
    otp = request.GET['otp']
    check_otp = Order.objects.filter(otp = otp).exists()
    if check_otp:
        data = {
            'incorrect_status' : 'correct_otp',
        }
        return JsonResponse(data)
    else :
        data = {
            'incorrect_status' : 'incorrect_otp',
            'check_otp' : check_otp,
        }
        return JsonResponse(data)

def user_pickup_orders_post(request):
    if request.method == 'POST':
        otp = request.POST['student_otp']
        request.session['otp'] = otp
        return redirect(user_pickup_orders)

def user_pickup_orders(request):
    store_id = request.session['store_id']
    otp = request.session['otp']
    store_object = Store.objects.get(id = store_id)
    orders = Order.objects.filter(otp = otp)
    return render(request,'tray/user_pickup_orders.html', {'orders': orders} )

def store_bills(request):
    store_id = request.session['store_id']
    store_object = Store.objects.get(id = store_id)
    store_bills = Bill.objects.filter(store = store_object)
    #sorted_orders = orders.order_by('student', 'pickup_time')
    return render(request,'tray/store_bills.html',{'store':store_object,'store_bills':store_bills})

def qr_code(request):
    return render(request, 'tray/qr_code.html')

#college views__________________________________________________________________________________
def register_college(request):
    return render(request, 'tray/register_college.html')

def register_college_success(request):
    if request.method == 'POST':
        college = request.POST['college_name']
        first_break = request.POST['first_break']
        lunch_break = request.POST['lunch_break']
        last_break = request.POST['last_break']
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        user = User.objects.create_user(username,email,password)
        user.save()
        institute = Institute(institute_name = college, user = user, )
        institute.save()
        break_time = Break(first_break = first_break, lunch_break = lunch_break, last_break = last_break, college = institute)
        break_time.save()
        return redirect(login_college)

def login_college(request):
    if request.user.is_authenticated:
        college_user = Institute.objects.filter(user = request.user).exists()
        if college_user:
            print("Already logged in")
            return redirect('college_home')
        else:
            return render (request, 'tray/login_college.html')
    else:
        return render (request, 'tray/login_college.html')

def college_login_verify(request):
    username = request.POST['username']
    password = request.POST['password']
    user = authenticate(request, username = username, password = password)
    user_institute_exist = Institute.objects.filter(user = user).exists()

    if user is not None and user_institute_exist:
        login(request, user)
        institute_id = user.institute.id
        request.session['institute_id'] = institute_id
        return redirect(college_home)
    else:
        c = "Sorry login failed!"
        return HttpResponse(c)   

def college_home(request):
    institute_id = request.session['institute_id']
    college = Institute.objects.get(id = institute_id)
    request.session['college_id'] = college.id
    stores = Store.objects.filter(college = college)

    return render(request,'tray/college_home.html', {'college': college, 'stores':stores})

def college_store_order_list_post(request):
    if request.method == 'POST':
        store_id = request.POST['store_id']
        request.session['store_id'] = store_id
        return redirect(college_store_order_list)

def college_store_order_list(request):
    store_id =  request.session['store_id']
    store_object = Store.objects.get(id = store_id)
    orders = Order.objects.filter(store = store_object)
    sorted_orders = orders.order_by('student', 'pickup_time')
    current_month = datetime.today().strftime("%h")
    current_month_number = datetime.today().month
    #month_total = orders.filter(created_at__month = current_month_number ).aggregate(Sum('cost'))
    month_orders = orders.filter(created_at__month = current_month_number )
    month_total = 0
    for order in month_orders:
        total = order.cost * order.quantity
        month_total = month_total + total 
    return render(request, 'tray/college_store_order_list.html', {'orders': sorted_orders,'store': store_object, 'current_month': current_month, 'month_total': month_total })

def college_break_edit(request):
    return render(request, 'tray/college_break_edit.html')

def college_break_edit_post(request):
    if request.method == 'POST':
        first_break = request.POST['first_break']
        lunch_break = request.POST['lunch_break']
        last_break = request.POST['last_break']
        college_id = request.session['college_id']
        college_object = Institute.objects.get(id=college_id)
        break_time_object = Break.objects.get(college = college_object)
        break_time_object.first_break = first_break
        break_time_object.lunch_break = lunch_break
        break_time_object.last_break = last_break
        break_time_object.save()
        return redirect (college_home)

def college_recharge(request):
    return render(request, 'tray/college_recharge.html')

def college_recharge_post(request):
    if request.method == 'POST':
        username = request.POST['username']
        student_object = Student.objects.get(name = username)
        student_name =  student_object.name
        student_balance = student_object.balance
    return render(request, 'tray/college_recharge_details.html', {'student_balance':student_balance, 'student_name':student_name})

def college_recharge_details(request):
    return render(request, 'tray/college_recharge_details.html')

def validate_recharge(request):
    username = request.GET['username']
    college_id = request.session['college_id']
    student_valid = Student.objects.filter(name = username, college = college_id).exists()
    if student_valid:
        data = {
            'username_status': "correct"
        } 
        return JsonResponse(data)


    else:
        data = {
            'username_status': "incorrect"
        }  
        return JsonResponse(data)
    


def college_recharge_final(request):
    username = request.GET['username']
    amount = request.GET['amount']
    student_object = Student.objects.get(name = username)
    current_balance = student_object.balance
    student_object.balance = current_balance + int(amount)
    student_object.save()
    data = {
        'recharge_status': "success",
        'present_balance': student_object.balance,
        'username': student_object.name,
    }
    return JsonResponse(data)


def college_logout(request):
    logout(request)
    return redirect(login_college)

# ajaxify with jquery views____________________________________________________________________
def validate_store_item(request):
    item_name = request.GET['item_name']
    data = {
        'is_taken': Item.objects.filter(item = item_name).exists()
    }
    return JsonResponse(data)

def validate_store_edit_item(request):
    item_name = request.GET['item_name']
    item_id = request.GET['item_id']
    data = {
        'is_taken': Item.objects.exclude(id = item_id).filter(item = item_name).exists()
    }
    return JsonResponse(data)


def add_new_store_item(request):
    return 
def update_store_status(request):
    store_open = request.GET['open']
    store_id = request.GET['store_id']
    store = Store.objects.get(id = store_id)
    
    if store_open == "Closed" :
        store.store_status = False
        store.save()
        data = {
            'is_open' : 'false'
        }
        return JsonResponse(data)

    elif store_open == "Open" :
        store.store_status = True
        store.save()
        data = {
            'is_open' : 'true'
        }

        return JsonResponse(data)


def update_item_availability(request):
    if request.GET['status'] == 'availability_change' :
        availability = request.GET['availability']
        item_id = request.GET['item_id']
        store_id = request.GET['store_id']
        store = Store.objects.get(id = store_id)
        item = Item.objects.get(id = item_id, store = store)
        if availability == 'available' :
            item.available = True
            item.save()
            data = {
                'available' : 'true'
            }
            return JsonResponse(data)

        elif availability == 'unavailable' :
            item.available = False
            item.save()
            data = {
                'available' : 'false'
            }
            return JsonResponse(data)

    if request.GET['status'] == 'delete_item' :
        item_id = request.GET['item_id']
        store_id = request.GET['store_id']
        store = Store.objects.get(id = store_id)
        if Item.objects.filter(id = item_id, store = store).exists() :
            item = Item.objects.get(id = item_id, store = store)
            item.delete()
            data = {
                'deleted' : 'true'
            }
            return JsonResponse(data)

        else :   
           data = {
               'deleted' : 'false'
           }
           return JsonResponse(data)

def validate_entry(request):
    username = request.GET['username']
    password = request.GET['password']
    user_exist = User.objects.filter(username = username).exists()
    if user_exist:
        user_student_exist = Student.objects.filter(name = username).exists()
    else: 
        user_student_exist = False

    if user_student_exist:
        user = User.objects.get(username = username)
        password_checker_bool = check_password(password,user.password)
        if (password_checker_bool== False):
            data = {
                'incorrect_status' : 'incorrect_password',
            }
        else :
            data = {
                'incorrect_status' : 'correct',
            }
        return JsonResponse(data)
    else :
        data = {
                'incorrect_status' : 'wrong_username'
            }
        return JsonResponse(data)

def validate_order_cancel(request):
    order_id = request.GET['order_id']
    order = Order.objects.get(id = order_id)
#'break_time_find' is variable which gives break name in string format from the respective order. eg. 'First Break'
    break_time_find = order.pickup_time
#this isn't hard code 'id = 1' there is only one break object for now will change and add relation
    break_object = Break.objects.get(college = order.student.college)
    if break_time_find == "First Break":
        break_time = break_object.first_break
    elif  break_time_find == "Lunch Break":
        break_time = break_object.lunch_break
    elif  break_time_find == "Last Break":
        break_time = break_object.last_break
    else: break_time = "Now"
    if order.status == True:
        data = {
                'cancelled' : 'already_delivered'
        }
        return JsonResponse(data)
    
    if  break_time == "Now" :
        student_balance = order.student.balance
        store_balance = order.store.store_balance
        student_balance = order.student.balance + order.cost
        order.student.balance = student_balance
        store_balance = order.store.store_balance - order.cost
        order.store.store_balance = store_balance
        order.student.save()
        order.store.save()
        order.delete()
        data = {
                'cancelled' : 'success'
            }
        return JsonResponse(data)
    else:
    #'break_time' contains the break time selected for the order
    #'cancel_time' is time when order is requested to be cancelled
        cancel_time = datetime.now()
        time_difference = break_time.hour - cancel_time.hour
        if time_difference >= 0 :
            student_balance = order.student.balance 
            student_balance = order.student.balance + order.cost
            order.student.balance = student_balance
            order.student.save()
            order.delete()

            data = {
                    'cancelled' : 'success'
                }
            return JsonResponse(data)
    
        elif time_difference < 1 :
            data = {
                    'cancelled' : 'failure'
                }
            return JsonResponse(data)

def cart(request):
    #block that adds items to cart
    student = False
    store = False
    if request.GET['status'] == 'add_to_cart':
        #can cache student and store object
        #no need to query them on each add_to_cart
        if student == False and store == False:
            student_id = request.GET['student_id']
            student = Student.objects.get(id = student_id)
            store_id = request.GET['store_id']
            store = Store.objects.get(id = store_id)
        item_name = request.GET['item_name']
        #time = request.GET['time']
        quantity = request.GET['quantity']
        
        if Item.objects.filter(item = item_name).exists() :
            item = Item.objects.get(item = item_name)
            price = item.price
            #cost = int(price) * int(quantity)
            #cart_item = CartItem(item = item_name, quantity = quantity, cost = cost, pickup_time = time, store = store, student = student )
            #cart_item.save()
            #item.save()
            data = {
                'added': 'success',
                'item_price' : price,
                #'time' : time,
            }
            return JsonResponse(data)
        else:
            data = {
                'added' : 'failure'
            }
            return JsonResponse(data)

    if request.GET['status'] == 'leaving_page':
        data = {
                'status' : 'cart_count_reset'
            }
        return JsonResponse(data)


    if request.GET['status'] == 'confirm_order':
        time = request.GET['time']
        store_id = request.GET['store_id']
        store = Store.objects.get(id = store_id)
        student_id = request.GET['student_id']
        total = request.GET['total']
        revenue = request.GET['revenue']
        student = Student.objects.get(id = student_id)
        #cart_items = CartItem.objects.filter(student = student)
        if  int(student.balance) > int(total) :
            #generating otp for the cart of items
            # generating random strings 
            # using random.choices()
            # initializing size of string 
            N = 4
            # using random.choices()
            # generating random strings 
            res = ''.join(random.choices(string.ascii_lowercase, k = N))
            otp = str(res)
            #taking orders as json
            load = json.loads(request.GET['order_list_json'])
            #passing json load to bulk create on orders db
            #creating bill orders on db
            objects = []
            new_object = []
            purchase_id = purchase_id_generator(store)
            for i in load:
                new_object = Order(item = i['item'],cost=i['price'], quantity = i['quantity'], pickup_time = time, otp=otp, store = store, student = student , revenue = revenue, purchase_id = purchase_id)
                #new_object = Bill(item=i['item'], price=i['price'], quantity=i['quantity'], invoice_no=new_invoice_no,invoice=file , store=store)
                objects.append(new_object)
                item = Item.objects.get(item = i['item'])
                #initializing stock of item variable
                item_stock = item.stock
                #updating stock at store
                item.stock = int(item_stock) - int(i['quantity'])
                item.save()
                #unticking item availability to customers on reaching low stock at store
                if item.stock < 5:
                    item.available = False
                    item.save()
                #updating store balance
                cost = i['quantity'] * i['price']
                store.store_balance = store.store_balance + cost
                store.save()
                #updating student balance
                student.balance = student.balance - cost
                student.save()
            #saving orders to db
            Order.objects.bulk_create(objects)

                    #for cart_item in cart_items :
                    #    item = Item.objects.get(item = cart_item.item)
                    #    #initializing stock of item variable
                    #    item_stock = item.stock
                    #    #saving the order from cart
                    #    order = Order(item = cart_item.item, quantity = cart_item.quantity, cost = cart_item.cost, pickup_time = cart_item.pickup_time, otp=otp, store = cart_item.store, student = cart_item.student )
                    #    order.save()
                        #updating stock at store
                    #    item.stock = int(item_stock) - int(cart_item.quantity)
                        #unticking item availability to customers on reaching low stock at store
                    #    if item.stock < 5:
                    #        item.available = False
                    #    item.save()
                    #updating store balance
                    #store.store_balance = store.store_balance + int(cart_item.cost)
                    #store.save()
                    #updating student balance
                    #student.balance = student.balance - int(cart_item.cost)
                    #student.save()
                    #deleting item from cart
                    #cart_item.delete()
                

            
            data = {
                    'status' : 'order_placed',
                    'cart_items' : False,
                    'total' : total,
                    'otp': otp,
                }
            return JsonResponse(data)

        elif int(student.balance) < int(total) :
            data = {
                'status' : 'low_balance'
            }
            return JsonResponse(data)

        

    if request.GET['status'] == 'delete_from_cart':
        item_id = request.GET['item_id']
        cart_item = CartItem.objects.get(id = item_id )
        cart_item.delete()
        data = {
                'status' : 'item_deleted'
            }
        return JsonResponse(data)

def purchase_id_generator(store):
            last_bill = Order.objects.filter(store = store).order_by('id').last()
            purchase_id = last_bill.purchase_id
            new_purchase_id = purchase_id + 1
            return new_purchase_id
        
        
def paytm(request):
    return render(request,'paytm_checkout.html')

def pickup_order(request):
    order_id = request.GET['order_id']
    order = Order.objects.get(id = order_id)
    order.status = True
    order.save()
    data = {
        'deliver' : 'true'
    }
    return JsonResponse(data)

def store_login_validate(request):
    user_name = request.GET['user_name']
    password = request.GET['password'] 
    user_exists = User.objects.filter(username=user_name).exists()
    if user_exists:
        user = User.objects.get(username=user_name)
        user_store_exist = Store.objects.filter(user = user).exists()
    else:
        user_store_exist = False

    if user_store_exist:
        password_check = check_password(password, user.password)
        if password_check:
            data = {
               'validity' : 'correct'
            }
            return JsonResponse(data)
        else:
            data = {
               'validity' : 'wrong_password'
            }
            return JsonResponse(data)
    else:
        data = {
               'validity' : 'invalid_user'
        }
        return JsonResponse(data)

def college_login_validate(request):
    user_name = request.GET['user_name']
    password = request.GET['password'] 
    user_exists = User.objects.filter(username=user_name).exists()
    if user_exists:
        user = User.objects.get(username=user_name)
        user_institute_exist = Institute.objects.filter(user = user).exists()
    else: 
        user_institute_exist = False
    
    if user_institute_exist:
        password_check = check_password(password, user.password)
        if password_check:
            data = {
               'validity' : 'correct'
            }
            return JsonResponse(data)
        else:
            data = {
               'validity' : 'wrong_password'
            }
            return JsonResponse(data)
    else:
        data = {
               'validity' : 'invalid_user'
        }
        return JsonResponse(data)

def store_register_validate(request):
    store_name = request.GET['store_name']
    college_id = request.GET['college_id']
    user_name = request.GET['user_name']
    college_object = Institute.objects.get(id = college_id)
    data = {
        'store_name_taken': Store.objects.filter(store_name = store_name, college = college_object).exists(),
        'user_name_taken' : User.objects.filter(username = user_name).exists()

    }
    return JsonResponse(data)

def store_edit_validate(request):
    store_name = request.GET['store_name']
    college_id = request.GET['college_id']
    store_id = request.GET['store_id']
    college_object = Institute.objects.get(id = college_id)
    data = {
        'store_name_taken': Store.objects.exclude(id = store_id).filter(store_name = store_name, college = college_object).exists()
    }
    return JsonResponse(data)

def college_register_validate(request):
    college_name = request.GET['college_name']
    user_name = request.GET['user_name']
    data = {
        'college_name_taken': Institute.objects.filter(institute_name = college_name).exists(),
        'user_name_taken' : User.objects.filter(username = user_name).exists()

    }
    return JsonResponse(data)

def student_register_validate(request):
    user_name = request.GET['user_name']
    password = request.GET['password']
    data = {
        'user_name_taken' : User.objects.filter(username = user_name).exists(),
    }
    return JsonResponse(data)

def student_pin_edit_validate(request):
    password = request.GET['password']
    student_id = request.GET['student_id']
    pin_no_hash = make_password(pin_no, 'pepper')
    data = {
        'pin_taken' : Student.objects.exclude(id = student_id).filter(pin_no = pin_no).exists(),
         }
    return JsonResponse(data)