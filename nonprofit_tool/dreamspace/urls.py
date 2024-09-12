from django.urls import path
from . import views

urlpatterns = [
    path('add-website/', views.add_website, name='add_website'),
    path('tag-autocomplete/', views.tag_autocomplete, name='tag_autocomplete'),
    path('list-website/', views.list_website, name='list_website'),
    path('list-logs/<int:website_id>/', views.list_logs, name='list_logs'),
]
