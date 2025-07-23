from django.urls import path
from . import views

app_name = 'colonybilling'

urlpatterns = [
    path('settings/fees/', views.association_fee_settings, name='association_fee_settings'),
    path('settings/fees/edit/<int:fee_id>/', views.association_fee_settings, name='edit_association_fee'),
    path('settings/fees/delete/<int:fee_id>/', views.delete_association_fee, name='delete_association_fee'),
    path('payments/', views.payment_list, name='payment-list'),
    path('payments/mark-paid/<int:pk>/', views.mark_payment_as_paid, name='mark-payment-as-paid'),
    path("advance-payment/", views.create_advance_payment, name="create-advance-payment"),

]
