from django.urls import path
from . import views

urlpatterns = [
    path('function-chat/', views.function_chat, name='function_chat'),
    path('function-convertion/', views.function_convertion, name='function_convertion'),
    path('write-functon-code/<int:function_Id>/', views.write_functon_code, name='write_functon_code'),
    path('write-models-code/<int:model_id>/<int:app_id>/', views.write_models_code, name='write_models_code'),

]