from django.urls import path
from . import views

urlpatterns = [
    path('testing-this-awesome-function/', views.testing_this_awesome_function, name='testing_this_awesome_function'),
    # Define URL patterns for the app here
]
