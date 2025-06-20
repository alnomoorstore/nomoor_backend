from django.urls import path
from .views import maintenance_form, records_view, edit_record, print_record, print_last_record, secure_device_detail, print_receipt_view

urlpatterns = [
    path('', maintenance_form, name='form'),
    path('records/', records_view, name='records'),
    path('edit/<int:record_id>/', edit_record, name='edit_record'),
    path('print/<int:record_id>/', print_record, name='print_record'),
    path('print-last/', print_last_record, name='print_last_record'),
    path('device/<str:serial>/', secure_device_detail, name='device_detail'),
    path('print/<str:serial>/', print_receipt_view, name='print_receipt'),
]
