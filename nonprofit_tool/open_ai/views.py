from django.http import JsonResponse
from dreamspace.models import WebSite, Tag, Log, App, Function, Models, Packages
from openai import OpenAI, APIError
from dotenv import load_dotenv
import instructor
from django.db import models
from django.utils.text import slugify
from typing import List
from pydantic import BaseModel, Field
import os
import re
import requests
import importlib.util
import json
import pkg_resources


load_dotenv()

# Initialize the OpenAI client
client = instructor.from_openai(OpenAI(api_key=os.getenv('OPENAI_API_KEY')))

class PackageInfo(BaseModel):
    import_statement: str

    @property
    def package_name(self) -> str:
        """Extract package name from the import statement."""
        if self.import_statement.startswith("import "):
            package_name = self.import_statement.split("import ")[1].split(" as ")[0].strip()
        elif self.import_statement.startswith("from "):
            package_name = self.import_statement.split("from ")[1].split(" import ")[0].strip()
        else:
            return ''
        return package_name

    @property
    def version(self) -> str:
        """Get package version."""
        try:
            version = pkg_resources.get_distribution(self.package_name).version
        except pkg_resources.DistributionNotFound:
            version = ''
        return version

    def install_command(self) -> str:
        """Generate install command."""
        response = requests.get(f"https://pypi.org/pypi/{self.package_name}/json")
        if response.status_code == 200:
            return f'pip install {self.package_name}'
        else:
            return ''


class PythonInfo(BaseModel):
    python: str
    packages: List[str] = Field(default_factory=list)
    confidence: float = Field(
        ge=0,  le=1, description='Confidence in is valid code' 
    )
    def __init__(self, **data):
        super().__init__(**data)
        # Validate and process the Python code
        if self.is_valid_code(self.python):
            self.packages = self.extract_packages(self.python)
            self.python = self.extract_code(self.python)
        else:
            raise ValueError("The provided string is not valid Python code or has fewer than 3 lines.")
        
    @staticmethod
    def is_valid_code(python_code: str) -> bool:
        """Check if the provided string is valid Python code with more than 2 lines."""
        lines = python_code.strip().splitlines()
        return len(lines) > 2

    @staticmethod
    def extract_packages(python_code: str) -> List[str]:
        """Extract Python packages from import statements."""
        import_pattern = re.compile(
            r'^\s*(import\s+\w+(?:\s+as\s+\w+)?|from\s+\w+(?:\.\w+)*\s+import\s+(?:\w+(?:\s*,\s*\w+)*)+)',
            re.MULTILINE
        )
        packages = []
        matches = import_pattern.findall(python_code)
        cleaned_matches = [match.strip() for match in matches]
        packages = [match.strip() for match in cleaned_matches]
        return packages
        
    @staticmethod
    def extract_code(python_code: str) -> str:
        """Extract Python code, excluding import statements and comments."""
        # Regular expression to match import statements
        import_pattern = re.compile(
            r'^\s*(import\s+\w+(?:\s+as\s+\w+)?|from\s+\w+(?:\.\w+)*\s+import\s+(?:\w+(?:\s*,\s*\w+)*)+)',
            re.MULTILINE
        )
        
        # Remove all comments (both full-line and inline comments)
        comment_pattern = re.compile(r'#.*')
        
        # Remove import statements
        matches = import_pattern.findall(python_code)
        lines = python_code.splitlines()
        
        # Filter lines that do not contain import statements and remove comments
        filtered_lines = []
        for line in lines:
            # Remove inline comments
            cleaned_line = comment_pattern.sub('', line).strip()
            if cleaned_line and not any(import_statement in line for import_statement in matches):
                filtered_lines.append(cleaned_line)
        
        # Join the filtered lines to form the final code string
        code = '\n'.join(filtered_lines).strip()
        return code


def is_package_installed(package_name):
    spec = importlib.util.find_spec(package_name)
    return spec is not None






def parse_model_string(model_str):
    """Extract model name and fields from the model string."""
    lines = model_str.strip().split('\n')
    model_name = lines[0].split('(')[0].strip()  # Extract model name
    fields = [line.strip() for line in lines[1:] if line.strip() and not line.strip().startswith('Meta')]
    return model_name, fields

def create_crud_code(model_name, fields):
    """Generate code for CRUD operations based on model name and fields."""
    try:
        fields_code = '\n    '.join(
            f'{name} = models.{typ}' 
            for field in fields 
            if ' = ' in field 
            for name, typ in [field.split(' = ', 1)]
        )
        
        add_code = f"""
def add_{slugify(model_name)}(request):
    try:
        data = request.POST
        {model_name}.objects.create(**data)
        return JsonResponse({{'success': True}})
    except Exception as e:
        return JsonResponse({{'success': False, 'error': str(e)}})
    """
        
        edit_code = f"""
def edit_{slugify(model_name)}(request, record_id):
    try:
        record = {model_name}.objects.get(id=record_id)
        data = request.POST
        for attr, value in data.items():
            setattr(record, attr, value)
        record.save()
        return JsonResponse({{'success': True}})
    except {model_name}.DoesNotExist:
        return JsonResponse({{'success': False, 'error': 'Record not found'}})
    except Exception as e:
        return JsonResponse({{'success': False, 'error': str(e)}})
    """
        
        delete_code = f"""
def delete_{slugify(model_name)}(request, record_id):
    try:
        record = {model_name}.objects.get(id=record_id)
        record.delete()
        return JsonResponse({{'success': True}})
    except {model_name}.DoesNotExist:
        return JsonResponse({{'success': False, 'error': 'Record not found'}})
    except Exception as e:
        return JsonResponse({{'success': False, 'error': str(e)}})
    """
        
        return add_code, edit_code, delete_code

    except Exception as e:
        print(f"Error creating CRUD code: {str(e)}")
        raise

def save_functions(model_name, add_code, edit_code, delete_code, app_id, model_id):
    """Store CRUD functions in the Function model."""
    
    try:
        app = App.objects.filter(id=app_id).first()
        model = Models.objects.filter(id=model_id).first()

        # Create 'add' function
        add_function = Function.objects.create(
            name=f'add_{slugify(model_name)}',
            description=f'Function to add a {model_name} record',
            python=add_code,
            app_relation=app
        )
        add_function.modeles_relation.add(model)  # Add relation to ManyToManyField

        # Create 'edit' function
        edit_function = Function.objects.create(
            name=f'edit_{slugify(model_name)}',
            description=f'Function to edit a {model_name} record',
            python=edit_code,
            app_relation=app
        )
        edit_function.modeles_relation.add(model)  # Add relation to ManyToManyField

        # Create 'delete' function
        delete_function = Function.objects.create(
            name=f'delete_{slugify(model_name)}',
            description=f'Function to delete a {model_name} record',
            python=delete_code,
            app_relation=app
        )
        delete_function.modeles_relation.add(model)  # Add relation to ManyToManyField

    except Exception as e:
        print(f"Error saving functions: {str(e)}")
        raise

def process_model(model_str, app_id, model_id):
    """Main function to process the model string and store CRUD functions."""
    try:
        model_name, fields = parse_model_string(model_str)
        add_code, edit_code, delete_code = create_crud_code(model_name, fields)
        save_functions(model_name, add_code, edit_code, delete_code, app_id, model_id)
    except Exception as e:
        print(f"Error processing model: {str(e)}")
        raise










def write_models_code(request, model_id, app_id):
    if request.method == 'POST':
        modelsPy = Models.objects.filter(id=model_id).first()
        try:
            code_info = client.chat.completions.create(
                model="gpt-4",
                max_retries= 3,
                response_model=PythonInfo,
                messages=[{"role": "user", "content": f"Please create Django models that {modelsPy.description}. Ensure the models include all necessary fields and relationships as described, and handle validation properly."}]
            )
            
            # Process each package and associate it with the function
            for match in code_info.packages:
                package_info = PackageInfo(import_statement=match)

                # Check if the package exists, if not create a new one
                package, created = Packages.objects.get_or_create(name=package_info.package_name, code=match, cmd=package_info.install_command(), version=package_info.version)
                
                # Add this Model to the package's modeles_relation
                package.modeles_relation.add(modelsPy)
                
                # Save the package (not strictly necessary if only adding a relation)
                package.save()    
            try:
                modelsPy.python = code_info.python
                modelsPy.save() 
            except Exception as e:
                print(f"Error saving model code: {str(e)}")
                return JsonResponse({'success': False, 'error': str(e)}, status=500)

            process_model(modelsPy.python, app_id, model_id)
        except Exception as e:
            print(f"Error in write_models_code: {str(e)}")
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
    
    return JsonResponse({'success': True})





def write_functon_code(request, function_Id):
    if request.method == 'POST':
        function = Function.objects.filter(id=function_Id).first()
        try:
            code_info = client.chat.completions.create(
                model="gpt-4",
                max_retries= 3,
                response_model=PythonInfo,
                messages=[{"role": "user", "content": f"Please write a Python function that performs the following task: {function.description}. The function should use JsonResponse to handle responses, and include all errors in the JsonResponse. Additionally, please provide a list of all Python packages used in the code."}],
            )
            # Process each package and associate it with the function
            for match in code_info.packages:
                package_info = PackageInfo(import_statement=match)

                # Check if the package exists, if not create a new one
                package, created = Packages.objects.get_or_create(name=package_info.package_name, code=match, cmd=package_info.install_command(), version=package_info.version)
                
                # Add this function to the package's function_relation
                package.function_relation.add(function)
                
                # Save the package (not strictly necessary if only adding a relation)
                package.save()            
            function.python = code_info.python
            function.save() 
        except Exception as e:
        
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
    
    return JsonResponse({'success': True})

































def function_chat(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        message = data.get('message')
        try:
            # OpenAI API call (assuming you've set up OpenAI API key in your environment)
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "user", "content": message},
                ]
            )
            return JsonResponse({'response': response.choices[0].message.content.strip()})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Invalid request method'}, status=405)

def function_convertion(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        conversation = data.get('conversation', [])
        # Prepare messages for OpenAI API
        try:
            response = client.chat.completions.create(
                model="gpt-4",
                messages=conversation
            )
            # Get the response message
            return JsonResponse({'response': response.choices[0].message.content.strip()})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request method'}, status=405)