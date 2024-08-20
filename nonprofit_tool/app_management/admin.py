# myapp/admin.py
from django.contrib import admin
from .models import App  # Import your models here

# Register your models here
admin.site.register(App)
