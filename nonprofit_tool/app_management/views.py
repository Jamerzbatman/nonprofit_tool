from django.core.management import call_command
from django.shortcuts import get_object_or_404
from .models import App, Payment, Function
from .forms import AppForm, AddFunctionForm
from django.template.loader import render_to_string
from rest_framework import serializers
import sys

import os, json
import django
import ast
import subprocess
import traceback
from django.conf import settings
from django.http import JsonResponse



def format_app_name(app_name):
    # Replace underscores with spaces and capitalize each word
    return app_name.replace('_', ' ').title()

def list_apps(request):
    apps = App.objects.all().values('id', 'name')
    
    # Format app names
    formatted_apps = [
        {
            'id': app['id'],
            'name': format_app_name(app['name'])
        }
        for app in apps
    ]
    
    return JsonResponse({'apps': formatted_apps})


def create_app(request):
    if request.method == 'POST':
        form = AppForm(request.POST)
        if form.is_valid():
            app_name = form.cleaned_data['name']
            app_description = form.cleaned_data['description']

            # Convert app_name to lowercase and replace spaces with underscores
            app_name = app_name.lower().replace(' ', '_')

            # Save the app details to the database
            new_app = App(name=app_name, description=app_description)
            new_app.save()

            # Run the management command to create the app
            try:
                call_command('create_custom_app', app_name, app_description)
                return JsonResponse({'success': True, 'app_id': new_app.id})
            except Exception as e:
                # Optionally, you can remove the app record from the database if the command fails
                new_app.delete()
                return JsonResponse({'success': False, 'error': str(e)})

        else:
            return JsonResponse({'success': False, 'errors': form.errors})
    else:
        return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=400)
    

def save_payment_details(request, app_id):
    if request.method == 'POST':
        app = App.objects.get(id=app_id)
        payment_type = request.POST.get('payment_type')
        amount = request.POST.get('amount')
        try:
            existing_payment = Payment.objects.filter(app=app, payment_type=payment_type).first()
            if payment_type == 'free':
                Payment.objects.filter(app=app).delete()
                Payment.objects.create(app=app, payment_type=payment_type, amount=00.00)
            elif not payment_type or not amount:
                return JsonResponse({'success': False, 'error': 'Missing payment type or amount'}, status=400)
            elif existing_payment:
                 existing_payment.amount = amount
                 existing_payment.save()

            elif payment_type == 'once':  
                Payment.objects.filter(app=app).delete()
                Payment.objects.create(app=app, payment_type=payment_type, amount=amount)
            else:
                free_payment = Payment.objects.filter(app=app, payment_type='free')
                if free_payment.exists():
                    free_payment.delete()
                once_payment = Payment.objects.filter(app=app, payment_type='once')
                if once_payment.exists():
                    once_payment.delete()
            

                Payment.objects.create(app=app, payment_type=payment_type, amount=amount)

            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=400)

def delete_payment(request, payment_id):
    if request.method == 'POST':
        try:
            payment = Payment.objects.get(id=payment_id)
            payment.delete()
            return JsonResponse({'success': True})
        except Payment.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Payment not found'}, status=404)
    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=400)


def fetch_payments(request, app_id):
    payments = Payment.objects.filter(app_id=app_id).values('id', 'payment_type', 'amount')
    return JsonResponse({'payments': list(payments)})


def fetch_model_details(request, app_id):
    
    app = get_object_or_404(App, id=app_id)
    app_name = app.name.lower().replace(' ', '_')

    # Path to the models.py file for the app
    models_file_path = os.path.join(settings.BASE_DIR, app_name, 'models.py')
    if os.path.exists(models_file_path):
        with open(models_file_path, 'r') as file:
            models_code = file.read()
        return JsonResponse({'models_code': models_code})
    else:
        return JsonResponse({'success': False, 'error': 'Models file not found'}, status=404)




def format_model_code(class_name, fields):
    """
    Formats the model code for a class with only the class definition and __str__ method.
    """
    # Add the class definition with proper class name
    model_code = ""
    model_code += f"class {class_name}\n"
    
    
    # Add the fields with proper indentation
    for field in fields:
        if field.strip():  # Avoid adding empty lines
            model_code += f"    {field.strip()}\n"

    # Add a __str__ method using the first field's name (if available)
    if fields:
        first_field_name = fields[1].split('=')[0].strip()  # Get the first field's name
        model_code += f"\n    def __str__(self):\n"
        model_code += f"        return f'{{self.{first_field_name}}}'\n"
    else:
        model_code += f"\n    def __str__(self):\n"
        model_code += f"        return 'Object'\n"

    return model_code

def extract_model_names(models_path):
    model_names = []
    try:
        with open(models_path, 'r') as file:
            file_content = file.read()
        
        # Parse the file content into an AST
        tree = ast.parse(file_content)
        
        # Extract class names that inherit from models.Model
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                # Check if the class inherits from models.Model
                if any(
                    isinstance(base, ast.Attribute) and base.attr == 'Model'
                    for base in node.bases
                ):
                    model_names.append(node.name)
                    
    except Exception as e:
        return f"Error extracting model names: {e}"

    return model_names

def generate_admin_code(model_names):
    
    if not model_names:
        return "from django.contrib import admin\n\n# No models to register."

    admin_code = "from django.contrib import admin\n"
    admin_code += "from .models import " + ", ".join(model_names) + "\n\n"
    admin_code += "# Register your models here.\n"

    for model_name in model_names:
        admin_code += f"admin.site.register({model_name})\n"
    

    
    return admin_code

def save_model_details(request, app_id):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            model_code = data.get('model_code')

            # Get the app and determine the app label
            app = get_object_or_404(App, id=app_id)
            app_label = app.name.lower()
            
            # Paths to models.py and admin.py
            models_path = os.path.join(settings.BASE_DIR, app_label, 'models.py')
            admin_path = os.path.join(settings.BASE_DIR, app_label, 'admin.py')
            
            # Write the model code to the models.py file
            with open(models_path, 'w') as file:
                file.write(model_code)

            # Extract model names from models.py
            model_names = extract_model_names(models_path)
            
            # Generate admin.py content
            admin_code = generate_admin_code(model_names)

            # Write the admin code to the admin.py file
            with open(admin_path, 'w') as file:
                file.write(admin_code)

            # Run Django management commands
            subprocess.run(['python3', 'manage.py', 'makemigrations'], check=True, cwd=settings.BASE_DIR)
            subprocess.run(['python3', 'manage.py', 'migrate'], check=True, cwd=settings.BASE_DIR)
            
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

def register_models_code(model_names):
    return '\n'.join([f'admin.site.register({model_name})' for model_name in model_names])

def save_class(request, app_id):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            app_id = data.get('appId')
            model_code_raw = data.get('modelCode')
            
            if not app_id or not model_code_raw:
                return JsonResponse({'success': False, 'error': 'App ID and model code are required'}, status=400)
            
            app = get_object_or_404(App, id=app_id)
            app_label = app.name.lower()
            models_path = os.path.join(settings.BASE_DIR, app_label, 'models.py')
            
            # Ensure the directory exists
            if not os.path.exists(os.path.dirname(models_path)):
                os.makedirs(os.path.dirname(models_path))
                        
            # Parse the raw model code to extract the class name and fields
            lines = model_code_raw.strip().split('\n')
            class_name = lines[0].split()[1]  # Extracts class name from "class ClassName(models.Model):"
            fields = lines[1:]  # The rest are the fields
            # Format the new class code
            new_model_code = format_model_code(class_name, fields)
            
            # Write the updated code to the file
            with open(models_path, 'a') as file:
                file.write("\n\n" + new_model_code)
            
            # Optionally reload models (if necessary)
            django.setup()

            return JsonResponse({'success': True})
        except Exception as e:
            # Log the detailed error for debugging
            error_message = traceback.format_exc()
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=405)


def add_function(request, app_id):
    app = get_object_or_404(App, pk=app_id)
    
    if request.method == 'POST':
        form = AddFunctionForm(request.POST)
        if form.is_valid():
            try:
                function = form.save(commit=False)
                function.app_relation = app
                function.save()
                return JsonResponse({'success': True})
            except Exception as e:
                return JsonResponse({'success': False, 'error': str(e)}, status=500)
        else:
            return JsonResponse({'success': False, 'error': form.errors.as_json()}, status=400)
    else:
        form = AddFunctionForm()
    
    form_html = render_to_string('functions/add_function.html', {'form': form, 'app': app}, request)
    return JsonResponse({'success': True, 'form_html': form_html})


def edit_function(request, function_id):
    function = get_object_or_404(Function, pk=function_id)
    
    if request.method == 'POST':
        form = AddFunctionForm(request.POST, instance=function)
        if form.is_valid():
            try:
                form.save()
                return JsonResponse({'success': True})
            except Exception as e:
                return JsonResponse({'success': False, 'error': str(e)}, status=500)
        else:
            return JsonResponse({'success': False, 'error': form.errors.as_json()}, status=400)
    else:
        form = AddFunctionForm(instance=function)

    form_html = render_to_string('functions/edit_function.html', {'form': form, 'function': function}, request)
    return JsonResponse({'success': True, 'form_html': form_html})

class FunctionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Function
        fields = ['id', 'name', 'description', 'parameters', 'return_type', 'code']

def manage_functions(request, app_id):
    app = get_object_or_404(App, pk=app_id)
    functions = Function.objects.filter(app_relation=app)
    
    functions_data = FunctionSerializer(functions, many=True).data
    
    return JsonResponse({'success': True, 'functions': functions_data})

def install_pip_package(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        package_name = data.get('package_name')

        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
            # Update the requirements.txt file
            requirements_path = os.path.join(settings.BASE_DIR, 'requirements.txt')
            with open(requirements_path, 'w') as f:
                subprocess.check_call([sys.executable, "-m", "pip", "freeze"], stdout=f)  
            
            return JsonResponse({'success': True})
        
        except subprocess.CalledProcessError as e:
            return JsonResponse({'success': False, 'error': str(e)})

    return JsonResponse({'success': False, 'error': 'Invalid request method'})

def get_installed_packages(request):
    try:
        result = subprocess.run([sys.executable, "-m", "pip", "freeze"], stdout=subprocess.PIPE, text=True)
        packages = result.stdout.splitlines()
        packages = [pkg.split('==')[0] for pkg in packages]  # Extract package names
        return JsonResponse({'success': True, 'packages': packages})
    except subprocess.CalledProcessError as e:
        return JsonResponse({'success': False, 'error': str(e)})