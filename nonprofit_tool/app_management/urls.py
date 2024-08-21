from django.urls import path
from . import views

urlpatterns = [
    path('list/', views.list_apps, name='list_apps'),    
    path('create/', views.create_app, name='create_app'),
    path('<int:app_id>/payment/', views.save_payment_details, name='save_payment_details'),
    path('fetch/<int:app_id>/payments/', views.fetch_payments, name='fetch_payments'),
    path('delete-payment/<int:payment_id>/', views.delete_payment, name='delete_payment'),
    path('fetch/<int:app_id>/models/', views.fetch_model_details, name='fetch_models'),
     path('<int:app_id>/save_models/', views.save_model_details, name='save_models'),
]
