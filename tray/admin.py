from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Permission, User

from users.models import User

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
    InstituteMerchantCredentail,
)

admin.site.register(Institute)
# admin.site.register(Student)
admin.site.register(InstituteMerchantCredentail)
admin.site.register(Item)
# admin.site.register(Store)
admin.site.register(Order)
admin.site.register(Break)
admin.site.register(CartItem)
admin.site.register(Bill)
admin.site.register(User)
admin.site.register(BulkRechargeMail)
# Register your models here for admin


class StudentAdmin(admin.ModelAdmin):
    search_fields = ("name",)


admin.site.register(Student, StudentAdmin)


class StoreAdmin(admin.ModelAdmin):
    search_fields = ("store_name",)


admin.site.register(Store, StoreAdmin)
