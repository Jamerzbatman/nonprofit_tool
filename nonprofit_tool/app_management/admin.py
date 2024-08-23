# myapp/admin.py
from django.contrib import admin
from .models import App, Payment, Function

admin.site.register(App)
admin.site.register(Payment)
admin.site.register(Function)
