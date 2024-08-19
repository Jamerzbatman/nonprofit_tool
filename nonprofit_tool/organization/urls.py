from django.urls import path
from . import views

urlpatterns = [
    path('add-edit-organization/', views.add_edit_organization, name='add_edit_organization'),
]