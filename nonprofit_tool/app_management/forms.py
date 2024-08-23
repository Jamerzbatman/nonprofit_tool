from django import forms
from .models import App, Payment, Function
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

class AddFunctionForm(forms.ModelForm):
    class Meta:
        model = Function
        fields = ['name', 'description', 'parameters', 'return_type', 'code']
        help_texts = {
            'name': 'Enter the name of the function.',
            'description': 'A brief description of what the function does.',
            'parameters': 'List the parameters this function accepts, e.g., x, y, z.',
            'return_type': 'Specify the function return type (e.g., int, string, JSON).',
            'code': 'Write the Python code that defines this function.',
        }
        widgets = {
            'code': forms.Textarea(attrs={'rows': 10, 'cols': 80, 'class': 'form-control'}),
        }

    def clean_code(self):
        code = self.cleaned_data.get('code')
        if not code:
            raise forms.ValidationError("Function code cannot be empty.")
        return code