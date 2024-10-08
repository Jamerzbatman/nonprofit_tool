from django.urls import path
from . import views

urlpatterns = [
    path('list/', views.list_apps, name='list_apps'),    
    path('create/', views.create_app, name='create_app'),
    path('<int:app_id>/payment/', views.save_payment_details, name='save_payment_details'),
    path('fetch/<int:app_id>/payments/', views.fetch_payments, name='fetch_payments'),
    path('delete-payment/<int:payment_id>/', views.delete_payment, name='delete_payment'),
    path('fetch/<int:app_id>/models/', views.fetch_model_details, name='fetch_models'),
    path('<int:app_id>/save_class/', views.save_class, name='save_class'),
    path('<int:app_id>/save_models/', views.save_model_details, name='save_models'),
    path('<int:app_id>/functions/', views.manage_functions, name='manage_functions'),
    path('<int:app_id>/functions/add/', views.add_function, name='add_function'),
    path('install-pip-package/', views.install_pip_package, name='install_pip_package'),
    path('get-models/<str:app_id>/', views.list_models_for_app, name='get_models_for_app'),
    path('get-model-definitions/<int:app_id>/', views.get_model_definitions, name='get_model_definitions'),
    path('function/<int:pk>/json/', views.function_detail_json, name='function_detail_json'),
    path('function/<int:pk>/edit/', views.function_edit, name='function_edit'),
]
