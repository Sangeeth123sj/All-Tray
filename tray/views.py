from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import Student,Item,Store,User,Order, Break, CartItem
from django.contrib.auth.models import User, Permission
from django.contrib.auth import authenticate, login
from .forms import LoginForm
from django.contrib import messages
from django.http import JsonResponse
from datetime import datetime




# Create your views here.
def entry(request):
    return render (request, 'tray/entry.html')

def register_card(request):
    if request.method == 'POST':
        student_name = request.POST['student_name']
        branch = request.POST['branch_name']
        semester = request.POST['semester']
        reg_no = request.POST['card']
        pin_no = request.POST['pin']
        student = Student(name = student_name, branch = branch, sem = semester, reg_no = reg_no, pin_no = pin_no)
        student.save()
        messages.success(request, 'Profile details updated.')
        return render (request, 'tray/entry.html')
    else:
        return render (request, 'tray/register_card.html')

def home(request):
    if request.method == 'POST':
        student_id = request.POST['student_id']
        student_pin = request.POST['student_pin']
        if student_pin:
            student = Student.objects.get(pin_no = student_pin)
        elif student_id:
            student = Student.objects.get(reg_no = student_id)
        stores = Store.objects.all()
        return render (request, 'tray/home.html', {'stores':stores, 'student': student, 'student_pin':student_pin})

def your_orders(request):
    if request.method == 'POST':
        student_id = request.POST['student_id']
        your_orders = Order.objects.filter(student = student_id )
        your_orders_now = Order.objects.filter(student = student_id, pickup_time = "Now")
        your_orders_first_break = Order.objects.filter(student = student_id, pickup_time = "First Break")
        your_orders_lunch_break = Order.objects.filter(student = student_id, pickup_time = "Lunch Break")
        your_orders_last_break = Order.objects.filter(student = student_id, pickup_time = "Last Break")
        return render(request, 'tray/your_orders.html', {'your_orders': your_orders, 'your_orders_now': your_orders_now, 'your_orders_first_break': your_orders_first_break, 'your_orders_lunch_break': your_orders_lunch_break, 'your_orders_last_break': your_orders_last_break})

def order_page(request):
    if request.method == 'POST':
        student_id = request.POST['student_id']
        store_name = request.POST['store_name']
        student = Student.objects.get(id = student_id)
        store = Store.objects.get(store_name = store_name)
        items = store.item_set.all()
    return render (request, 'tray/order_page.html', {'student': student, 'store': store, 'items': items})

def order(request):
    store_id = request.session['store_id']
    
    return render (request, 'tray/order.html',{'store_id': store_id})

def order_placed(request):
#   if request.method == 'POST':
#      student_id = request.POST['student_id']
#        store_id = request.POST['store_id']
#        student = Student.objects.get(id = student_id)
#        store = Store.objects.get(id = store_id)
#        pickup_time = request.POST['time']
#        item_name = request.POST['item_name']
#        quantity = request.POST['quantity']
#        item = Item.objects.get(item=item_name)
#        price = item.price
#        cost = int(price) * int(quantity)
#        order = Order(item1 = item_name, stock = quantity, cost1 = cost, Time = pickup_time, store = store, Student = student )
#        order.save()


   return render (request, 'tray/order_placed.html' )

def order_items(request):
    if request.method == 'POST':
        name = request.POST['order']
        quantity = request.POST['quantity']
        store_id = request.POST['store_id']
        price = request.POST['price']
        store_object = Store.objects.get(id = store_id)
        new_item = Item(item = name, quantity = quantity, price = price, store = store_object)
        new_item.save()
    return redirect(store_home)

def open_store(request):
    return render(request, 'tray/open_store.html' )

def open_store_success(request):
    if request.method == 'POST':
        name = request.POST['store_name']
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        user = User.objects.create_user(username,email,password)
        user.save()
        s = Store(store_name= name, store_status = True, user = user)
        s.save()
        return redirect(store_login)

def store_home(request):
    store_id = request.session['store_id']
    s = Store.objects.get(id = store_id)
    store_name = s.store_name
    items = s.item_set.all()
    status = s.store_status
    request.session['store_id'] = store_id
    
    if status == True:
        c = "Open"
    else:
        c = "Closed"

    return render(request, 'tray/store_home.html',{'store_name':store_name, 'status':c, 'items':items})

def store_login(request):
    return render(request, 'tray/login_store.html' )


def store_login_processing(request):
    username = request.POST['username']
    password = request.POST['password']
    user = authenticate(request, username = username, password = password)

    if user is not None:
        login(request, user)
        store_id = user.store.id
        request.session['store_id'] = store_id
        return redirect(store_home)
    else:
        c = "Sorry login failed!"
        return HttpResponse(c)   

def logout(request):
    logout(request)
    return render(request,'tray/logged_out.html')

def store_order_list(request):
    store_id = request.session['store_id']
    store_object = Store.objects.get(id = store_id)
    orders = Order.objects.filter(store = store_object)
    return render(request, 'tray/store_order_list.html',{'orders': orders}) 

def form_test(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            return HttpResponse("form test success, POST")
    else:
        form = LoginForm()

    return render(request, 'tray/test_form.html', {'form': form})

# ajaxify with jquery functions

def validate_store_item(request):
    item_name = request.GET['order']
    data = {
        'is_taken': Item.objects.filter(item = item_name).exists()
    }
    return JsonResponse(data)

def update_store_status(request):
    store_open = request.GET['open']
    store = Store.objects.get(id = 1)

    if store_open == "Closed" :
        store.store_status = False
        store.save()
        data = {
            'is_open' : 'false'

        }

    elif store_open == "Open" :
        store.store_status = True
        store.save()
        data = {
            'is_open' : 'true'
        }
    return JsonResponse(data)

def validate_entry(request):
    pin = request.GET['pin']
    id_card = request.GET['id_card']
    # converting pin and id_card to int make it compatible for filter query
    if pin == "":
        pin = 0
    if id_card == "":
        id_card = 0

    check_card = bool(Student.objects.filter(reg_no = id_card))
    check_pin = bool(Student.objects.filter(pin_no = pin))
    if (check_card == False) and (check_pin == False):
        data = {
            'incorrect_pin_or_card' : 'incorrect',
            'check_card' : check_card,
            'check_pin' : check_pin
        }
    else :
        data = {
            'incorrect_pin_or_card' : 'caught in else',
            'check_card' : check_card,
            'check_pin' : check_pin
        }
    return JsonResponse(data)


def validate_order_cancel(request):
    order_id = request.GET['order_id']
    order = Order.objects.get(id = order_id)
    #'break_time_find' is variable which gives break name in string format from the respective order. eg. 'First Break'
    break_time_find = order.pickup_time
    #this isn't hard code 'id = 1' there is only one break object for now will change and add relation
    break_object = Break.objects.get(id = 1)
    if break_time_find == "First Break":
        break_time = break_object.first_break
    elif  break_time_find == "Lunch Break":
        break_time = break_object.lunch_break
    elif  break_time_find == "Last Break":
        break_time = break_object.last_break
    #'break_time' contains the break time selected for the order
    #'cancel_time' is time when order is requested to be cancelled
    cancel_time = datetime.now()
    time_difference = break_time.hour - cancel_time.hour
    if time_difference >= 0 :
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





subtotal = 0

def cart(request):
    global subtotal
    
#block that adds items to cart
    if request.GET['status'] == 'add_to_cart':
        item_name = request.GET['item_name']
        student_id = request.GET['student_id']
        student = Student.objects.get(id = student_id)
        store_id = request.GET['store_id']
        store = Store.objects.get(id = store_id)
        time = request.GET['time']
        quantity = request.GET['quantity']
        

        if Item.objects.filter(item = item_name).exists() :
            item = Item.objects.get(item = item_name)
            price = item.price
            cost = int(price) * int(quantity)

            cart_item = CartItem(item = item_name, quantity = quantity, cost = cost, pickup_time = time, store = store, student = student )
            cart_item.save()
            total = cost + subtotal
            subtotal = cost
            data = {
                'added': 'success',
                'item_price' : price,
                'time' : time,
                'total' : total
            }
            
            return JsonResponse(data)
        else:
            data = {
                'added' : 'failure'
            }
            return JsonResponse(data)

    
    if request.GET['status'] == 'leaving_page':
        
        student_id = request.GET['student_id']
        student = Student.objects.get(id = student_id)
        cart_items = CartItem.objects.filter(student = student)
        for item in cart_items :
            item.delete()
        
        data = {
                'status' : 'cart_count_reset'
            }
        return JsonResponse(data)


    if request.GET['status'] == 'confirm_order':

        student_id = request.GET['student_id']
        student = Student.objects.get(id = student_id)
        cart_items = CartItem.objects.filter(student = student)
        for item in cart_items :
            order = Order(item = item.item, quantity = item.quantity, cost = item.cost, pickup_time = item.pickup_time, store = item.store, student = item.student )
            order.save()
            item.delete()

        data = {
                'status' : 'order_placed'
            }
        return JsonResponse(data)
