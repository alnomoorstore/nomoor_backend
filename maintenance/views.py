from django.shortcuts import render, redirect, get_object_or_404
from .models import MaintenanceRecord
from django import forms
from django.db.models import Q
from datetime import datetime
from django.http import HttpResponse
from django.template.loader import render_to_string

class MaintenanceForm(forms.ModelForm):
    class Meta:
        model = MaintenanceRecord
        exclude = ['serial']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 🟢 1. منع التعديل على وقت الاستلام
        self.fields['date_time'].disabled = True
        # 🕒 2. جعل وقت التسليم على شكل مؤقت زمني (time picker)
        self.fields['delivery_time'].widget = forms.DateTimeInput(
            attrs={'type': 'datetime-local'}
        )

class EditFieldsForm(forms.ModelForm):
    class Meta:
        model = MaintenanceRecord
        fields = ['device', 'maintenance_type', 'issue', 'price', 'status']

def maintenance_form(request):
    if request.method == 'POST':
        form = MaintenanceForm(request.POST)
        if form.is_valid():
            current = form.cleaned_data
            exists = MaintenanceRecord.objects.filter(
                name=current['name'],
                phone=current['phone'],
                device=current['device'],
                issue=current['issue'],
                employee=current['employee'],
                receiver=current['receiver'],
                notes=current['notes'],
                price=current['price'],
                status=current['status'],
                delivery_time=current['delivery_time'],
                date_time__date=datetime.today().date()
            ).exclude(maintenance_type=current['maintenance_type'])

            if exists.exists():
                form.save()
                return redirect('form')  # تأكد من الاسم الصحيح هنا
            else:
                form.add_error(None, 'تم إدخال نفس البيانات سابقاً بدون تغيير نوع الصيانة.')
    else:
        form = MaintenanceForm()
    
    return render(request, 'maintenance/form.html', {'form': form})

def edit_record(request, record_id):
    record = get_object_or_404(MaintenanceRecord, id=record_id)
    if request.method == 'POST':
        form = EditFieldsForm(request.POST, instance=record)
        if form.is_valid():
            form.save()
            return redirect('records')
    else:
        form = EditFieldsForm(instance=record)
    return render(request, 'maintenance/edit_record.html', {'form': form})

def records_view(request):
    maintenance_type = request.GET.get('type')
    if maintenance_type:
        records = MaintenanceRecord.objects.filter(maintenance_type=maintenance_type)
    else:
        records = MaintenanceRecord.objects.all()

    return render(request, 'maintenance/records.html', {'records': records})

def print_record(request, record_id):
    record = MaintenanceRecord.objects.get(id=record_id)
    html = render_to_string('maintenance/print.html', {'record': record})
    return HttpResponse(html)

def print_last_record(request):
    try:
        record = MaintenanceRecord.objects.latest('id')
    except MaintenanceRecord.DoesNotExist:
        return HttpResponse("لا يوجد سجل حتى الآن.")

    html = render_to_string('maintenance/print.html', {'record': record})
    return HttpResponse(html)

from django.shortcuts import get_object_or_404

def device_detail(request, serial):
    record = get_object_or_404(MaintenanceRecord, serial=serial)
    return render(request, 'maintenance/device_detail.html', {'record': record})

def print_receipt_view(request, serial):
    record = get_object_or_404(MaintenanceRecord, serial=serial)
    return render(request, 'maintenance/print.html', {'record': record})

def secure_device_detail(request, serial):
    record = get_object_or_404(MaintenanceRecord, serial=serial)
    return render(request, 'maintenance/device_detail.html', {'record': record})
