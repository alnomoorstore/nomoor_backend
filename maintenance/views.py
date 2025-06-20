from django.shortcuts import render, redirect, get_object_or_404
from .models import MaintenanceRecord
from django import forms
from django.db.models import Q
from datetime import datetime
from django.http import HttpResponse, HttpResponseNotFound
from django.template.loader import render_to_string
from .forms import SaveDeviceForm  # استيراد الفورم الجديد هنا
from django.contrib import messages
from django.urls import reverse

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
    if not request.session.get('device_saved'):
        return redirect('save_device')

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
            ).filter(maintenance_type=current['maintenance_type'])

            if exists.exists():
                form.add_error(None, 'تم إدخال نفس البيانات سابقاً بنفس نوع الصيانة.')
            else:
                form.save()
                messages.success(request, "تم حفظ البيانات بنجاح.")
                return redirect('form')  # إعادة تحميل الصفحة أو أي صفحة تريدها
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
    records = MaintenanceRecord.objects.all()
    maintenance_types = records.values_list('maintenance_type', flat=True).distinct().order_by('maintenance_type')

    # بناء قاموس الحالات لكل نوع صيانة
    status_map = {}
    for m_type in maintenance_types:
        status_map[m_type] = list(
            records.filter(maintenance_type=m_type)
                   .values_list('status', flat=True)
                   .distinct()
                   .order_by('status')
        )

    return render(request, 'maintenance/records.html', {
        'records': records,
        'maintenance_types': maintenance_types,
        'status_map': status_map,
        'selected_maintenance_type': request.GET.get('type', ''),
        'selected_status': request.GET.get('status', '')
    })

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

from django.shortcuts import get_object_or_404, render

def device_detail_view(request, serial):
    record = get_object_or_404(MaintenanceRecord, serial=serial)
    return render(request, 'maintenance/device_detail.html', {'record': record})

def print_receipt_view(request, serial):
    # بناء رابط كامل للجهاز
    device_url = request.build_absolute_uri(reverse('device_detail', args=[serial]))
    record = get_object_or_404(MaintenanceRecord, serial=serial)
    context = {
        'device_url': device_url,
        'record': record,
    }
    return render(request, 'maintenance/print.html', context)

def secure_device_detail(request, serial):
    record = get_object_or_404(MaintenanceRecord, serial=serial)
    return render(request, 'maintenance/device_detail.html', {'record': record})

def print_receipt(request, serial):
    try:
        record = MaintenanceRecord.objects.get(serial=serial)
    except MaintenanceRecord.DoesNotExist:
        return HttpResponseNotFound("لم يتم العثور على السجل")
    # Render قالب الطباعة مع البيانات record
    return render(request, 'maintenance/print.html', {'record': record})

# ممكن تخزن الأجهزة المحفوظة في الجلسة أو بالقاعدة حسب احتياجك
def save_device_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        # افحص اسم المستخدم وكلمة السر، غيرها حسب ما تريد
        if username == 'nomoor' and password == 'NR7777300nr':
            request.session['device_saved'] = True
            messages.success(request, "تم حفظ الجهاز بنجاح")
            return redirect('form')  # بعد الحفظ رجع للصفحة الرئيسية أو حسب حاجتك
        else:
            messages.error(request, "خطأ في اسم المستخدم أو كلمة السر")
            return redirect('save_device')
    return render(request, 'maintenance/save_device.html')

from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages

def delete_record(request, record_id):
    record = get_object_or_404(MaintenanceRecord, id=record_id)
    if request.method == "POST":
        record.delete()
        messages.success(request, "تم حذف السجل بنجاح.")
        return redirect('records')
    else:
        messages.error(request, "لا يمكن حذف السجل عبر طلب GET.")
        return
