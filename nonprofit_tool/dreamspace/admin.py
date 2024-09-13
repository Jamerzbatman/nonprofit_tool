from django.contrib import admin

from .models import WebSite, WebSiteVersion, Tag, Log, App

admin.site.register(WebSite)
admin.site.register(App)
admin.site.register(WebSiteVersion)
admin.site.register(Tag)
admin.site.register(Log)


