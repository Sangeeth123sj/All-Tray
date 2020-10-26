from django.shortcuts import render
from django.http import HttpResponse
from .models import Student,Item,Store
from django.contrib.auth.models import User, Permission
from django.contrib.auth import authenticate, login

# Create your views here.

def index(request, name_id):
    s = Student.objects.get(id = name_id)
    return HttpResponse("Hello django, you are seeing student %s." %s.name )

def home(request):
    return render (request, 'tray/home.html')

def order(request, name_id):
    s = Student.objects.get(id = name_id)
    name = s.name
    reg_no = s.reg_no
    balance = s.balance
    return render (request, 'tray/order.html', {'name': name, 'reg': reg_no, 'balance': balance, 'student_id':name_id})

def order_items(request):
    if request.method == 'POST':
        name = request.POST['order']
        quantity = request.POST['quantity']
        t = Item(item1 = name, quantity1 = quantity)
        t.save()
        student_id = request.POST['balance'] 
        s = Student.objects.get(id = student_id)
        bal = s.balance - 10
        s.balance = bal
        s.save()
    return HttpResponse("Order saved! balance: %s." %s.balance)

def open_store(request):
    
    return render(request, 'tray/open_store.html' )

def store_home(request, store_id):
    if request.method == 'POST':
        name = request.POST['store_name']
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        user = User.objects.create_user(username,email,password)
        user.save()
        s = Store(store_name= name, store_status = True)
        s.save()
        status = s.store_status
        if status == True:
            c = "Active"
        else:
            c = "Inactive"

    else:
        s = Store.objects.get(id = store_id)
        name = s.store_name
        status = s.store_status
        if status == True:
            c = "Active"
        else:
            c = "Inactive"

    return render(request, 'tray/store_home.html',{'name':name, 'status':c})

def store_login(request):
    return render(request, 'tray/login_store.html' )


def store_login_processing(request):
    username = request.POST['username']
    password = request.POST['password']
    user = authenticate(request, username = username, password = password)

    if user is not None:
        login(request, user)
        return render(request, 'tray/store_home.html')
    else:
        c = "Sorry login failed!"
        return HttpResponse(c)
    
    

def user_reg(request):
    user = User.objects.create_user('sanga','sangeeth@gmail.com','123')
    user.save()
    return HttpResponse("user sang created")

