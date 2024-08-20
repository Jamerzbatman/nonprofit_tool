from django.core.management.base import BaseCommand
import subprocess
import os

class Command(BaseCommand):
    help = 'Creates a new Django app, adds it to INSTALLED_APPS, updates urls.py, and creates a urls.py file in the app'

    def add_arguments(self, parser):
        parser.add_argument('name', type=str, help='Name of the new app')
        parser.add_argument('description', type=str, help='Description of the new app')

    def handle(self, *args, **kwargs):
        name = kwargs['name']
        description = kwargs['description']
        
        # Create the new app
        subprocess.run(['django-admin', 'startapp', name], check=True)

        # Update INSTALLED_APPS in settings.py
        settings_file = 'config/settings.py'  # Adjust path if necessary
        
        # Read current settings
        with open(settings_file, 'r') as f:
            settings_content = f.read()

        # Check if the app is already in INSTALLED_APPS
        if f"'{name}'" not in settings_content:
            # Update INSTALLED_APPS list
            with open(settings_file, 'w') as f:
                # Insert the new app into INSTALLED_APPS
                updated_content = settings_content.replace(
                    'INSTALLED_APPS = [',
                    f"INSTALLED_APPS = [\n    '{name}',"
                )
                f.write(updated_content)

        # Update urlpatterns in urls.py
        urls_file = 'config/urls.py'
        
        with open(urls_file, 'r') as f:
            urls_content = f.read()

        # Check if the URL pattern is already present
        if f"path('{name}/', include('{name}.urls'))" not in urls_content:
            # Add the new app's URL pattern
            with open(urls_file, 'w') as f:
                updated_content = urls_content.replace(
                    'urlpatterns = [',
                    f"urlpatterns = [\n    path('{name}/', include('{name}.urls')),"
                )
                f.write(updated_content)

        # Create urls.py in the new app
        app_urls_file = os.path.join(name, 'urls.py')
        with open(app_urls_file, 'w') as f:
            f.write(
                """from django.urls import path
from . import views

urlpatterns = [
    # Define URL patterns for the app here
]
"""
            )

        # Run migrations for the new app
        os.chdir(name)
        
        # Return to the root directory
        os.chdir('..')

        self.stdout.write(self.style.SUCCESS(f'Successfully created and configured app "{name}"'))
