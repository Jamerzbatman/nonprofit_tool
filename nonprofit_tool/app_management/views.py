from django.core.management import call_command
from .models import App
from .forms import AppForm
from django.http import JsonResponse



def app_list(request):
    apps = App.objects.all()

def create_app(request):
    if request.method == 'POST':
        form = AppForm(request.POST)
        if form.is_valid():
            app_name = form.cleaned_data['name']
            app_description = form.cleaned_data['description']

            # Save the app details to the database
            new_app = App(name=app_name, description=app_description)
            new_app.save()

            # Run the management command to create the app
            try:
                call_command('create_custom_app', app_name, app_description)
                return JsonResponse({'success': True, 'app_id': new_app.id})
            except Exception as e:
                # Optionally, you can remove the app record from the database if command fails
                new_app.delete()
                return JsonResponse({'success': False, 'error': str(e)})

        else:
            return JsonResponse({'success': False, 'errors': form.errors})
    else:
        return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=400)