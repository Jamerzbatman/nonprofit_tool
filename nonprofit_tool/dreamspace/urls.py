from django.urls import path
from . import views

urlpatterns = [
    path('add-website/', views.add_website, name='add_website'),
    path('add-app-to-dreamspace/', views.add_app_to_dreamspace, name='add_app_to_dreamspace'),
    path('add-function-to-app/', views.add_function_to_app, name='add_function_to_app'),
    path('add-model-to-app/', views.add_model_to_app, name='add_model_to_app'),
    path('add-app-to-website/', views.add_app_to_website, name='add_app_to_website'),
    path('tag-autocomplete/', views.tag_autocomplete, name='tag_autocomplete'),
    path('list-website/', views.list_website, name='list_website'),
    path('list-global-apps/<int:website_id>/', views.list_global_apps, name='list_global_apps'),
    path('list-logs/<int:website_id>/', views.list_logs, name='list_logs'),
    path('list-apps/<int:website_id>/', views.list_app, name='list_app'),
    path('list-app-data/<int:app_id>/', views.list_app_data, name='list_app_data'),
    path('fetch-website/<int:website_id>/', views.fetch_website, name='fetch_website'),


]
