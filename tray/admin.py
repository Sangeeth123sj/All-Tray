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
    SubscriptionPlans,
    FeePayment,
    InstituteMerchantCredentail,
    InstituteEvent
)


admin.site.register(SubscriptionPlans)
admin.site.register(InstituteEvent)
# admin.site.register(Student)
# admin.site.register(InstituteMerchantCredentail)
# admin.site.register(Item)
# admin.site.register(Store)
# admin.site.register(Order)
# admin.site.register(Break)
# admin.site.register(CartItem)
# admin.site.register(Bill)
admin.site.register(OrderGroup)

# admin.site.register(BulkRechargeMail)
# Register your models here for admin


class InstituteMerchantCredentailAdmin(ImportExportMixin, admin.ModelAdmin):
    search_fields = ("college",)
    list_per_page=10
admin.site.register(InstituteMerchantCredentail,InstituteMerchantCredentailAdmin)

class ItemAdmin(ImportExportMixin, admin.ModelAdmin):
    search_fields = ("store__store_name",)
    list_per_page=10
admin.site.register(Item,ItemAdmin)

class OrderAdmin(ImportExportMixin, admin.ModelAdmin):
    search_fields = ("student__name","created_at")
    list_per_page=10
admin.site.register(Order,OrderAdmin)

class BreakAdmin(ImportExportMixin, admin.ModelAdmin):
    search_fields = ("college__institute_name",)
    list_per_page=10
admin.site.register(Break,BreakAdmin)

class CartItemAdmin(ImportExportMixin, admin.ModelAdmin):
    search_fields = ("store__store_name","student__name")
    list_per_page=10
admin.site.register(CartItem,CartItemAdmin)

class BillAdmin(ImportExportMixin, admin.ModelAdmin):
    search_fields = ("created_at","store__store_name","student__name")
    list_per_page=10
admin.site.register(Bill,BillAdmin)


class BulkRechargeMailAdmin(ImportExportMixin, admin.ModelAdmin):
    search_fields = ("college__institute_name","student__name")
    list_per_page=10
admin.site.register(BulkRechargeMail,BulkRechargeMailAdmin)

class UserAdmin(ImportExportMixin, admin.ModelAdmin):
    search_fields = ("email",)
    list_per_page=10
admin.site.register(User,UserAdmin)


class FeePaymentAdmin(ImportExportMixin, admin.ModelAdmin):
    search_fields = ("student__name",)
admin.site.register(FeePayment,FeePaymentAdmin)

class RevenueAdmin(ImportExportMixin, admin.ModelAdmin):
    search_fields = ("student__name",)
    list_per_page=10
admin.site.register(Revenue,RevenueAdmin)


class InstituteAdmin(ImportExportMixin, admin.ModelAdmin):
    search_fields = ("institute_name",)
    list_per_page=10
admin.site.register(Institute,InstituteAdmin)


class StudentAdmin(ImportExportMixin,admin.ModelAdmin):
    search_fields = ("name",)
    list_per_page=10
admin.site.register(Student, StudentAdmin)


class StoreAdmin(ImportExportMixin,admin.ModelAdmin):
    search_fields = ("store_name",)
    list_per_page=10
admin.site.register(Store, StoreAdmin)
