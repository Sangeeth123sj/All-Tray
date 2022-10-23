from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Permission, User
from import_export.admin import ImportExportMixin



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
    Revenue,
    OrderGroup,
)



# admin.site.register(Student)
admin.site.register(InstituteMerchantCredentail)
admin.site.register(Item)
# admin.site.register(Store)
admin.site.register(Order)
admin.site.register(Break)
admin.site.register(CartItem)
admin.site.register(Bill)
admin.site.register(OrderGroup)

admin.site.register(BulkRechargeMail)
# Register your models here for admin

class UserAdmin(ImportExportMixin, admin.ModelAdmin):
    search_fields = ("email",)

admin.site.register(User,UserAdmin)

class RevenueAdmin(ImportExportMixin, admin.ModelAdmin):
    search_fields = ("student",)

admin.site.register(Revenue,RevenueAdmin)


class InstituteAdmin(ImportExportMixin, admin.ModelAdmin):
    search_fields = ("institute_name",)

admin.site.register(Institute,InstituteAdmin)


class StudentAdmin(ImportExportMixin,admin.ModelAdmin):
    search_fields = ("name",)

admin.site.register(Student, StudentAdmin)


class StoreAdmin(ImportExportMixin,admin.ModelAdmin):
    search_fields = ("store_name",)

admin.site.register(Store, StoreAdmin)
