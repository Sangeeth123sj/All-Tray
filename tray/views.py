from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import Student,Item,Store,User,Order, Break, CartItem, Institute
from django.db.models import Sum
from django.contrib.auth.models import User, Permission
from django.contrib.auth import authenticate, login
from .forms import LoginForm
from django.contrib.auth import logout
from django.contrib import messages
from django.http import JsonResponse
from datetime import datetime
from datetime import timedelta
from django.contrib.auth.hashers import check_password, make_password



#student views______________________________________________________________________________

def register_card(request):
    colleges = Institute.objects.all()
    return render(request, 'tray/register_card.html', {'colleges': colleges})

def register_card_post(request):
    if request.method == 'POST':
        student_name = request.POST['student_name']
        branch = request.POST['branch_name']
        semester = request.POST['semester']
        reg_no = request.POST['card']
        reg_no_hash = make_password(reg_no, 'pepper')
        pin_no = request.POST['pin']
        pin_no_hash = make_password(pin_no, 'pepper')
        college_id = request.POST['college_id']
        email = request.POST['mail_id']
        college_object = Institute.objects.get(id = college_id)
        user = User.objects.create_user(student_name,email,pin_no)
        user.save
        student = Student(name = student_name, branch = branch, sem = semester, reg_no = reg_no_hash, pin_no = pin_no_hash, college = college_object, user = user)
        student.save()
        messages.success(request, 'Profile details updated.')
        return render (request, 'tray/entry.html')

def entry(request):

    if request.user.is_active:
        print("Already logged in")
        return redirect('home')
    else:
        return render (request, 'tray/entry.html')

def home_post(request):
    if request.method == 'POST':
        student_id = request.POST['student_id']
        student_pin = request.POST['student_pin']
        request.session['student_id'] = student_id
        request.session['student_pin'] = student_pin
        return redirect(home)

def home(request):
    student_id_post = request.session['student_id']
    student_pin_post = request.session['student_pin']
    if student_pin_post:
        user = authenticate(request, pin_no = student_pin_post)
    elif student_id_post:
        user = authenticate(request, reg_no = student_id_post)
    
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
        return render(request, 'tray/your_orders.html', {'orders': orders})

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
        pin_no = request.POST['pin_no']
        student = Student.objects.get(id = student_id)
        student.pin_no = make_password (pin_no, 'pepper')
        student.save()
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
    return render(request, 'tray/login_store.html' )


def store_login_processing(request):
    username = request.POST['username']
    password = request.POST['password']
    user = authenticate(request, username = username, password = password)

    if user is not None:
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
    month_total = orders.filter(created_at__month = current_month_number ).aggregate(Sum('cost'))
    return render(request, 'tray/store_order_list.html',{'orders': sorted_orders, 'current_month': current_month, 'month_total': month_total}) 

def store_item_pickup(request):
    store_id = request.session['store_id']
    request.session['store_id'] = store_id 
    return render(request, 'tray/store_item_pickup.html')

def user_pickup_orders_post(request):
    if request.method == 'POST':
        student_id = request.POST['student_id']
        student_pin = request.POST['student_pin']
        request.session['student_id'] = student_id
        request.session['student_pin'] = student_pin
        return redirect(user_pickup_orders)

def user_pickup_orders(request):
    store_id = request.session['store_id']
    student_id = request.session['student_id']
    student_pin = request.session['student_pin']
    store_object = Store.objects.get(id = store_id)
    if student_pin:
        student_pin_hash = make_password(student_pin,'pepper')
        student = Student.objects.get(pin_no = student_pin_hash)
    elif student_id:
        student_id_hash = make_password(student_id,'pepper')
        student = Student.objects.get(reg_no = student_id_hash)
    orders = Order.objects.filter(store = store_object, student = student)
    return render(request,'tray/user_pickup_orders.html', {'orders': orders, 'student': student} )

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
    return render (request, 'tray/login_college.html')

def college_login_verify(request):
    username = request.POST['username']
    password = request.POST['password']
    user = authenticate(request, username = username, password = password)

    if user is not None:
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
    month_total = orders.filter(created_at__month = current_month_number ).aggregate(Sum('cost'))
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
    pin = request.GET['pin']
    id_card = request.GET['id_card']
    pin_hash = make_password(pin,'pepper')
    id_card_hash = make_password(id_card, 'pepper')
    check_card = bool(Student.objects.filter(reg_no = id_card_hash))
    check_pin = bool(Student.objects.filter(pin_no = pin_hash))
    if (check_card == False) and (check_pin == False):
        data = {
            'incorrect_pin_or_card' : 'incorrect',
            'check_card' : check_card,
            'check_pin' : check_pin
        }
    else :
        data = {
            'incorrect_pin_or_card' : 'correct',
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
    break_object = Break.objects.get(college = order.student.college)
    if break_time_find == "First Break":
        break_time = break_object.first_break
    elif  break_time_find == "Lunch Break":
        break_time = break_object.lunch_break
    elif  break_time_find == "Last Break":
        break_time = break_object.last_break
    else: break_time = "Now"

    if  break_time == "Now" :
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
            item.save()
            data = {
                'added': 'success',
                'item_price' : price,
                'cart_item_id' : cart_item.id,
                'time' : time,
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
        store_id = request.GET['store_id']
        store = Store.objects.get(id = store_id)
        student_id = request.GET['student_id']
        total = request.GET['total']
        student = Student.objects.get(id = student_id)
        cart_items = CartItem.objects.filter(student = student)
        if cart_items.exists() and int(student.balance) > int(total) :
            for cart_item in cart_items :
                item = Item.objects.get(item = cart_item.item)
                #updating stock at store
                item_stock = item.stock
                item.stock = int(item_stock) - int(cart_item.quantity)
                #unticking item availability to customers on reaching low stock at store
                if item.stock < 5:
                    item.available = False
                item.save()
                #updating store balance
                store.store_balance = store.store_balance + int(cart_item.cost)
                store.save()
                #updating student balance
                student.balance = student.balance - int(cart_item.cost)
                student.save()
                order = Order(item = cart_item.item, quantity = cart_item.quantity, cost = cart_item.cost, pickup_time = cart_item.pickup_time, store = cart_item.store, student = cart_item.student )
                order.save()
                cart_item.delete()
            data = {
                    'status' : 'order_placed',
                    'cart_items' : cart_items.exists(),
                    'total' : total
                }
            return JsonResponse(data)
        
        elif cart_items.exists() and int(student.balance) < int(total) :
            data = {
                'status' : 'low_balance'
            }
            return JsonResponse(data)

        elif cart_items.exists() == False:
            data = {
                    'status' : 'no_item_in_cart',
                    'cart_items' : cart_items.exists()
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
    pin_no = request.GET['pin']
    card_id = request.GET['card']
    pin_no_hash = make_password(pin_no, 'pepper')
    card_id_hash = make_password(card_id, 'pepper')
    data = {
        'user_name_taken' : User.objects.filter(username = user_name).exists(),
        'pin_taken' : Student.objects.filter(pin_no = pin_no_hash).exists(),
        'card_taken' : Student.objects.filter(reg_no = card_id_hash).exists(),

    }
    return JsonResponse(data)

def student_pin_edit_validate(request):
    pin_no = request.GET['pin_no']
    student_id = request.GET['student_id']
    pin_no_hash = make_password(pin_no, 'pepper')
    data = {
        'pin_taken' : Student.objects.exclude(id = student_id).filter(pin_no = pin_no_hash).exists(),
         }
    return JsonResponse(data)