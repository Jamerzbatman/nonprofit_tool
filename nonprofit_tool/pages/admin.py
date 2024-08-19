from django.contrib import admin
from .models import Page, Placeholder

@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'template_name')

@admin.register(Placeholder)
class PlaceholderAdmin(admin.ModelAdmin):
    list_display = ('page', 'name', 'text_value', 'image_value')
    list_filter = ('page',)
    search_fields = ('name', 'text_value')
