from django.urls import path

from . import views

urlpatterns = [
    path('<int:name_id>/', views.index, name='index'),
    path('', views.home, name='home'),
    path('order/<int:name_id>/', views.order, name = 'order'),
    path('order_items/', views.order_items, name = 'order_items'),
    path('register_store/', views.open_store, name = 'open_store'),
    path('store_home/<int:store_id>/', views.store_home, name = 'store_home'),
]