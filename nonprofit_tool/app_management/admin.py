# myapp/admin.py
from django.contrib import admin
from .models import App, Payment

admin.site.register(App)
admin.site.register(Payment)

