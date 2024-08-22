from django.apps import AppConfig


class SomethingNewConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'something_new'
