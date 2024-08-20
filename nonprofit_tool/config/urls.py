from django.conf.urls.static import static
from django.urls import path, include
from django.conf import settings
from django.contrib import admin


urlpatterns = [
    path('admin/', admin.site.urls),
    path('apps/', include('app_management.urls')),
    path('campaigns/', include('campaigns.urls')),
    path('dashboard/', include('dashboard.urls')),
    path('organization/', include('organization.urls')),
    path('questionnaires/', include('questionnaires.urls')),
    path('administration/', include('administration.urls')),
    path('', include('base.urls')),
    path('', include('pages.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

