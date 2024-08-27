from django.urls import path
from . import views

urlpatterns = [
    path('function-chat/', views.function_chat, name='function_chat'),
    path('function-convertion/', views.function_convertion, name='function_convertion'),
]

