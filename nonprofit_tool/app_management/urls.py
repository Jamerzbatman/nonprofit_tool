from django.urls import path
from . import views

urlpatterns = [
    path('list/', views.list_apps, name='list_apps'),    
    path('create/', views.create_app, name='create_app'),
    path('<int:app_id>/payment/', views.save_payment_details, name='save_payment_details'),
    path('fetch/<int:app_id>/payments/', views.fetch_payments, name='fetch_payments'),
]
