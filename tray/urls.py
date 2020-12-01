from django.urls import path

from . import views

urlpatterns = [
    path('', views.entry, name='entry'),
    path('register_card/', views.register_card, name='register_card'),
    path('home/', views.home, name='home'),
    path('your_orders/', views.your_orders, name='your_orders'),
    path('order_page/', views.order_page, name='order_page'),
    path('order_placed/', views.order_placed, name='order_placed'),
    path('store_add_item/', views.order, name = 'order'),
    path('order_items/', views.order_items, name = 'order_items'),
    path('register_store/', views.open_store, name = 'open_store'),
    path('register_store_success/', views.open_store_success, name = 'open_store_success'),
    path('store_home/', views.store_home, name = 'store_home'),
    path('login/', views.store_login, name = 'store_login'),
    path('login_verify/', views.store_login_processing, name = 'store_login_processing' ),
    path('logout/', views.logout, name='logout'),
    path('form_test/', views.form_test, name = 'form_test'),
    path('store_order_list/', views.store_order_list, name='store_order_list'),
    #ajaxify using jquery
    path('ajax/validate_store_item/', views.validate_store_item, name='validate_store_item'),
    path('ajax/update_store_status/', views.update_store_status, name = 'update_store_status'),
    path('ajax/validate_entry/', views.validate_entry, name = 'validate_entry'),
    path('ajax/validate_order_cancel/', views.validate_order_cancel, name = 'validate_order_cancel'),
    path('ajax/cart/', views.cart, name = 'cart'),
]