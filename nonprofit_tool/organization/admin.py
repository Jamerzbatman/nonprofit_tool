from django.contrib import admin
from .models import Organization

@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'created')  # Fields shown in the list view
    search_fields = ('name', 'user__username')  # Allows searching by organization name and username
    list_filter = ('created',)  # Adds a filter sidebar by creation date
    ordering = ('-created',)  # Orders the list by creation date, descending
