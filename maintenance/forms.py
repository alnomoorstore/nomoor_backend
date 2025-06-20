from django import forms

class SaveDeviceForm(forms.Form):
    username = forms.CharField(label="اسم المستخدم", max_length=100)
    password = forms.CharField(label="كلمة المرور", widget=forms.PasswordInput)

