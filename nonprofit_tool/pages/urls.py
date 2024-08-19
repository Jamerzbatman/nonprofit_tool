from django.conf.urls.static import static
from django.urls import path
from django.conf import settings
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),  # Replace 'scripts_view' with your actual view function name
    path('list-templates/', views.list_templates, name='list_templates'),
    path('add-page/', views.add_page, name='add_page'),
    path('get-placeholders/', views.get_placeholders, name='get_placeholders'),
    path('list-pages/', views.list_pages, name='list_pages'),
    path('get-page-data/', views.get_page_data, name='get_page_data'),
    path('update-placeholders/<int:page_id>/', views.update_placeholders, name='update_placeholders'),
    path('edit-template/<str:template_name>/', views.edit_template, name='edit_template'),
    path('add-template/', views.add_template, name='add_template'),
    path('get-template-content/', views.get_template_content, name='get_template_content'),
    path('<slug:slug>/', views.dynamic_page, name='dynamic_page'),
    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
