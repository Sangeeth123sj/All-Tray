from django.shortcuts import render
from django.http import HttpResponse
from .models import Student,Items
from tray.forms import OrderForm
# Create your views here.

def index(request, name_id):
    s = Student.objects.get(id = name_id)
    return HttpResponse("Hello django, you are seeing student %s." %s.name )

def home(request):
    return render (request, 'tray/home.html')

def order(request, name_id):
    id_of = Student.objects.get(id = name_id)
    name = id_of.name
    reg_no = id_of.reg_no
    return render (request, 'tray/order.html', {'name': name, 'reg': reg_no})

def order_items(request):
    if request.method == 'POST':
        name = request.POST['order']
        quantity = request.POST['quantity']
        t = Items(item = name, quantity = quantity)
        t.save()
    return HttpResponse("Order saved! item: %s." %t.quantity)