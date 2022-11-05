from django.urls import path
from .views import initiate_payment, callback, fee_payment

urlpatterns = [
    path('fee_payment/', fee_payment, name='fee_payment'),
    path('pay/', initiate_payment, name='pay'),
    path('callback/<str:merchant_token>/<str:student_token>/<str:payment_type>', callback, name='callback'),
]
