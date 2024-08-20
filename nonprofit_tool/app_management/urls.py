from django.urls import path
from . import views

urlpatterns = [
    path('list/', views.list_apps, name='list_apps'),    
    path('create/', views.create_app, name='create_app'),
]
