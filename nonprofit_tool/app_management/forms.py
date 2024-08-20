from django import forms
from .models import App, Payment
from django.forms import inlineformset_factory

class AppForm(forms.ModelForm):
    class Meta:
        model = App
        fields = ['name', 'description']

class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['payment_type', 'amount']

PaymentFormSet = inlineformset_factory(App, Payment, form=PaymentForm, extra=1, can_delete=True)