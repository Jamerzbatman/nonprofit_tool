from django.urls import path
from . import views

urlpatterns = [
    path('new-1/', views.new_1, name='new_1'),
    path('new/', views.new, name='new'),
    # Define URL patterns for the app here
]
