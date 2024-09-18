from django.contrib import admin

from .models import WebSite, WebSiteVersion, Tag, Log, App, Function, Packages,Models

admin.site.register(WebSite)
admin.site.register(App)
admin.site.register(WebSiteVersion)
admin.site.register(Tag)
admin.site.register(Log)
admin.site.register(Function)
admin.site.register(Packages)
admin.site.register(Models)

