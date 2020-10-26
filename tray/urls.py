from django.urls import path

from . import views

urlpatterns = [
    path('<int:name_id>/', views.index, name='index'),
    path('', views.home, name='home'),
    path('order/<int:name_id>/', views.order, name = 'order'),
    path('order_items/', views.order_items, name = 'order_items'),
    path('register_store/', views.open_store, name = 'open_store'),
    path('store_home/<int:store_id>/', views.store_home, name = 'store_home'),
    path('register_test/', views.user_reg, name = 'user_reg'),
    path('login/', views.store_login, name = 'store_login'),
    path('login_verify/', views.store_login_processing, name = 'store_login' )
]