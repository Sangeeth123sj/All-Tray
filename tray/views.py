from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import Student,Item,Store,User
from django.contrib.auth.models import User, Permission
from django.contrib.auth import authenticate, login

# Create your views here.

def index(request, name_id):
    s = Student.objects.get(id = name_id)
    return HttpResponse("Hello django, you are seeing student %s." %s.name )

def home(request):
    stores = Store.objects.all()
    return render (request, 'tray/home.html', {'stores':stores})

def order_page(request):
    if request.method == 'POST':
        student_id = request.POST['student_id']
        store_name = request.POST['store_name']
        student = Student.objects.get(id = student_id)
        store = Store.objects.get(store_name = store_name)
        items = store.item_set.all()

        loop = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    return render (request, 'tray/order_page.html', {'student': student, 'store': store, 'items': items, 'loop': loop})

def order(request):
    store_id = request.session['store_id']
    
    return render (request, 'tray/order.html',{'store_id': store_id})

def order_items(request):
    if request.method == 'POST':
        name = request.POST['order']
        quantity = request.POST['quantity']
        store_id = request.POST['store_id']
        store_object = Store.objects.get(id = store_id)
        new_item = Item(item = name, quantity = quantity, store = store_object)
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
        c = "Active"
    else:
        c = "Inactive"

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
    
    

def user_reg(request):
    user = User.objects.create_user('sanga','sangeeth@gmail.com','123')
    user.save()
    return HttpResponse("user sang created")

