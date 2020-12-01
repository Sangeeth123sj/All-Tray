from django.contrib import admin
from .models import Student, Item, Store, Order, Institute, Break, CartItem
admin.site.register(Institute)
admin.site.register(Student)
admin.site.register(Item)
admin.site.register(Store)
admin.site.register(Order)
admin.site.register(Break)
admin.site.register(CartItem)
# Register your models here for admin
