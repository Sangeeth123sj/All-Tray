from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path
from django.views.generic import TemplateView

from . import views

urlpatterns = [
    path("register_card/", views.register_card, name="register_card"),
    path("register_card_post/", views.register_card_post, name="register_card_post"),
    path("", views.entry, name="entry"),
    path("home_post/", views.home_post, name="home_post"),
    path("home/", views.home, name="home"),
    path("college_merchant_creds_form/", views.college_merchant_creds_form, name="college_merchant_creds_form"),
    path("your_orders_post/", views.your_orders_post, name="your_orders_post"),
    path("your_orders/", views.your_orders, name="your_orders"),
    path("order_page_post/", views.order_page_post, name="order_page_post"),
    path("order_page/", views.order_page, name="order_page"),
    path("store_add_item/", views.store_add_item, name="store_add_item"),
    path("store_add_item_save/", views.store_add_item_save, name="store_add_item_save"),
    path("edit_items_post/", views.edit_items_post, name="edit_items_post"),
    path("edit_items/", views.edit_items, name="edit_items"),
    path("edit_item_save/", views.edit_item_save, name="edit_item_save"),
    path("register_store/", views.open_store, name="open_store"),
    path(
        "register_store_success/", views.open_store_success, name="open_store_success"
    ),
    path("store_home/", views.store_home, name="store_home"),
    path("store_billing/", views.store_billing, name="billing"),
    path("login/", views.store_login, name="store_login"),
    path("login_verify/", views.store_login_processing, name="store_login_processing"),
    path("store_logout/", views.store_logout, name="store_logout"),
    path("college_logout/", views.college_logout, name="college_logout"),
    path("student_logout/", views.student_logout, name="student_logout"),
    path("store_edit_details/", views.store_edit_details, name="store_edit_details"),
    path(
        "store_edit_details_post/",
        views.store_edit_details_post,
        name="store_edit_details_post",
    ),
    path("store_order_list/", views.store_order_list, name="store_order_list"),
    path("store_item_pickup/", views.store_item_pickup, name="store_item_pickup"),
    path(
        "user_pickup_orders_post/",
        views.user_pickup_orders_post,
        name="user_pickup_orders_post",
    ),
    path("user_pickup_orders/", views.user_pickup_orders, name="user_pickup_orders"),
    path("store_bills/", views.store_bills, name="store_bills"),
    path("register_college/", views.register_college, name="register_college"),
    path(
        "register_college_success/",
        views.register_college_success,
        name="register_college_success",
    ),
    path("login_college/", views.login_college, name="login_college"),
    path(
        "college_login_verify/", views.college_login_verify, name="college_login_verify"
    ),
    path("college_home/", views.college_home, name="college_home"),
    # path("college_merchant_creds_post/", views.college_merchant_creds_post, name="college_merchant_creds_post"),
    path(
        "college_bulk_recharge/",
        views.college_bulk_recharge,
        name="college_bulk_recharge",
    ),
    path(
        "college_store_order_list_post/",
        views.college_store_order_list_post,
        name="college_store_order_list_post",
    ),
    path(
        "college_store_order_list/",
        views.college_store_order_list,
        name="college_store_order_list",
    ),
    path("college_break_edit/", views.college_break_edit, name="college_break_edit"),
    path(
        "college_break_edit_post/",
        views.college_break_edit_post,
        name="college_break_edit_post",
    ),
    path("college_recharge/", views.college_recharge, name="college_recharge"),
    path(
        "college_recharge_post/",
        views.college_recharge_post,
        name="college_recharge_post",
    ),
    path(
        "college_recharge_details/",
        views.college_recharge_details,
        name="college_recharge_details",
    ),
    path("student_pin_edit/", views.student_pin_edit, name="student_pin_edit"),
    path(
        "student_pin_edit_post/",
        views.student_pin_edit_post,
        name="student_pin_edit_post",
    ),
    path("paytm/", views.paytm, name="paytm"),
    path("invoice_print/", views.invoice_print, name="invoice_print"),
    path("qr_code/", views.qr_code, name="qr_code"),
    # ajaxify using jquery_____________________________________________________________________________________________
    path(
        "ajax/validate_store_item/",
        views.validate_store_item,
        name="validate_store_item",
    ),
    path(
        "ajax/validate_store_edit_item/",
        views.validate_store_edit_item,
        name="validate_store_edit_item",
    ),
    path(
        "ajax/update_store_status/",
        views.update_store_status,
        name="update_store_status",
    ),
    path(
        "ajax/update_item_availability/",
        views.update_item_availability,
        name="update_item_availability",
    ),
    path("ajax/validate_entry/", views.validate_entry, name="validate_entry"),
    path(
        "ajax/validate_order_cancel/",
        views.validate_order_cancel,
        name="validate_order_cancel",
    ),
    path("ajax/cart/", views.cart, name="cart"),
    path("ajax/pickup_order/", views.pickup_order, name="pickup_order"),
    path(
        "ajax/store_login_validate/",
        views.store_login_validate,
        name="store_login_validate",
    ),
    path(
        "ajax/college_login_validate/",
        views.college_login_validate,
        name="college_login_validate",
    ),
    path(
        "ajax/store_register_validate/",
        views.store_register_validate,
        name="store_register_validate",
    ),
    path(
        "ajax/college_register_validate/",
        views.college_register_validate,
        name="college_register_validate",
    ),
    path(
        "ajax/student_register_validate/",
        views.student_register_validate,
        name="student_register_validate",
    ),
    path(
        "ajax/store_edit_validate/",
        views.store_edit_validate,
        name="store_edit_validate",
    ),
    path(
        "ajax/student_pin_edit_validate/",
        views.student_pin_edit_validate,
        name="student_pin_edit_validate",
    ),
    path(
        "ajax/store_item_pickup_validate/",
        views.store_item_pickup_validate,
        name="store_item_pickup_validate",
    ),
    path("ajax/validate_recharge/", views.validate_recharge, name="validate_recharge"),
    path(
        "ajax/college_recharge_final/",
        views.college_recharge_final,
        name="college_recharge_final",
    ),
    path("ajax/billing/item_price/", views.billing_item_price, name="item_price"),
    path("ajax/billing/invoice/", views.billing_invoice, name="billing_invoice"),
    path(
        "ajax/bulk_recharge/", views.bulk_recharge_submit, name="bulk_recharge_submit"
    ),
    path(
        "ajax/home_store_status_update/",
        views.home_store_status_update,
        name="home_store_status_update",
    ),
]
# + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
