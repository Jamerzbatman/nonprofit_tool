# myapp/admin.py
from django.contrib import admin
from .models import App, Payment, Function, FunctionVersion

admin.site.register(App)
admin.site.register(Payment)
admin.site.register(Function)
admin.site.register(FunctionVersion)

