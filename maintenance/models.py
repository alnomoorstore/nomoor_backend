from django.db import models
import uuid
from django.utils import timezone

class MaintenanceRecord(models.Model):
    MAINTENANCE_CHOICES = [
        ('صيانة هواتف', '📱 صيانة هواتف'),
        ('صيانة تجميعات', '💻 صيانة تجميعات'),
        ('صيانة أجهزة الألعاب', '🎮 صيانة أجهزة الألعاب'),
    ]

    STATUS_CHOICES = [
        ('قيد الفحص', '🔍 قيد الفحص'),
        ('قيد الصيانة', '🛠️ قيد الصيانة'),
        ('جاهز للاستلام', '✅ جاهز للاستلام'),
        ('تم التسليم', '📦 تم التسليم'),
    ]

    serial = models.CharField(max_length=100, unique=True, editable=False, default=uuid.uuid4)
    name = models.CharField("اسم الزبون", max_length=100)
    phone = models.CharField("رقم الهاتف", max_length=20)
    price = models.CharField("السعر", max_length=100)
    issue = models.CharField("نوع العطل", max_length=200)
    device = models.CharField("نوع الجهاز", max_length=100)
    maintenance_type = models.CharField("نوع الصيانة", max_length=100, choices=MAINTENANCE_CHOICES)
    employee = models.CharField("اسم الموظف", max_length=100)
    receiver = models.CharField("موظف الاستلام", max_length=100)
    date_time = models.DateTimeField("وقت الاستلام", default=timezone.now)
    delivery_time = models.DateTimeField("وقت التسليم")
    status = models.CharField("حالة الجهاز", max_length=50, choices=STATUS_CHOICES)
    notes = models.TextField("ملاحظات", blank=True)

    def __str__(self):
        return f"{self.serial} - {self.name}"
