from django.contrib import admin

from .models import WebSite, WebSiteVersion, Tag

admin.site.register(WebSite)
admin.site.register(WebSiteVersion)
admin.site.register(Tag)
