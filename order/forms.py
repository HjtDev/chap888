from django import forms
from .models import Order


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = (
            'first_name', 'last_name', 'email',
            'phone', 'province', 'city',
            'address', 'postal_code', 'notes'
        )

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if not phone:
            raise forms.ValidationError('شماره تلفن مورد نیاز است.')
        if len(phone) != 11:
            raise forms.ValidationError('شماره تلفن باید 11 رقم باشد.')
        if not phone.isdigit():
            raise forms.ValidationError('شماره تلفن فقط شامل اعداد می باشد.')
        if not phone.startswith('09'):
            raise forms.ValidationError('شماره تلفن باید با 09 آفاز شود.')

        return phone

    def clean_postal_code(self):
        code = self.cleaned_data.get('postal_code')
        if not code:
            return code
        if len(code) < 10:
            raise forms.ValidationError('کد پستی معتبر نمی باشد.')
        if not code.isdigit():
            raise forms.ValidationError('کد پستی فقط شامل اعداد می باشد.')
        return code



