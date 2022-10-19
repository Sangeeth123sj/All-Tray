from django.urls import path
from .views import initiate_payment, callback

urlpatterns = [
    path('pay/', initiate_payment, name='pay'),
    path('callback/<str:merchant_key>/<str:student_key>', callback, name='callback'),
]
