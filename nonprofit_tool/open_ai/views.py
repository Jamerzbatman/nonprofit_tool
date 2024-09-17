from django.http import JsonResponse
from dreamspace.models import WebSite, Tag, Log, App, Function, Models
from openai import OpenAI, APIError
from dotenv import load_dotenv
import instructor
from pydantic import BaseModel
import os
import re
import json


import json

load_dotenv()

# Initialize the OpenAI client
client = instructor.from_openai(OpenAI(api_key=os.getenv('OPENAI_API_KEY')))

class PythonInfo(BaseModel):
    python: str

def write_functon_code(request, function_Id):
    if request.method == 'POST':
        function = Function.objects.filter(id=function_Id).first()
        try:
            code_info = client.chat.completions.create(
                model="gpt-4",
                response_model=PythonInfo,
                messages=[{"role": "user", "content": f"Please write Python function that {function.description}. Ensure the code uses JsonResponse to handle responses and includes all errors in the JsonResponse."}],
            )
            # Regex pattern to match import statements accurately
            import_pattern = re.compile(
                r'^\s*(import\s+\w+(?:\s+as\s+\w+)?|from\s+\w+(?:\.\w+)*\s+import\s+(?:\w+(?:\s*,\s*\w+)*)+)',
                re.MULTILINE
            )
            
            # Find all matches
            matches = import_pattern.findall(code_info.python)
            
            # Clean up the matches and remove any additional whitespace
            cleaned_matches = [match.strip() for match in matches]

            lines = code_info.python.splitlines()
            filtered_lines = [line for line in lines if not any(import_statement in line for import_statement in matches)]
            function.packages = json.dumps(cleaned_matches)
            function.python = '\n'.join(filtered_lines).strip()
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