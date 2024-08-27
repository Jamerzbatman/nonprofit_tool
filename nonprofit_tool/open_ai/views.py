from django.http import JsonResponse
from openai import OpenAI, APIError
from dotenv import load_dotenv
import os


import json

load_dotenv()

# Initialize the OpenAI client
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))


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