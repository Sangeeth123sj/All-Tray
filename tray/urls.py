from django.urls import path

from . import views

urlpatterns = [
    path('<int:name_id>/', views.index, name='index'),
    path('', views.home, name='home'),
    path('store_add_item/', views.order, name = 'order'),
    path('order_items/', views.order_items, name = 'order_items'),
    path('register_store/', views.open_store, name = 'open_store'),
    path('register_store_success/', views.open_store_success, name = 'open_store_success'),
    path('store_home/', views.store_home, name = 'store_home'),
    path('register_test/', views.user_reg, name = 'user_reg'),
    path('login/', views.store_login, name = 'store_login'),
    path('login_verify/', views.store_login_processing, name = 'store_login_processing' )
]