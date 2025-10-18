from django.urls import path
from . import views

app_name = 'payment'

urlpatterns = [
    path('payment/<int:pet_id>/', views.payment_page, name='payment_page'),
    path('khalti/verify/', views.khalti_verify, name='khalti_verify'),
    path('esewa/verify/', views.esewa_verify, name='esewa_verify'),
    path('esewa/signature/', views.get_esewa_signature, name='get_esewa_signature'),
    path('success/', views.payment_success, name='payment_success'),
    path('failed/', views.payment_failed, name='payment_failed'),
]