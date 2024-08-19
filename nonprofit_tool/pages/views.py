from django.template.exceptions import TemplateDoesNotExist
from django.shortcuts import render, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from pages.models import Page, Placeholder
from django.http import JsonResponse
from pages.forms import PageForm
from django.conf import settings
import os
import re





def home_view(request):
    # Fetch the page with slug 'home_page' from the database
    page = get_object_or_404(Page, slug='home_page')

    # Fetch all the placeholders related to this page
    placeholders = Placeholder.objects.filter(page=page)
    
    navbar_pages = Page.objects.filter(show_in_navbar=True)
    # Build a context with placeholders (populate dynamically)
    context = {placeholder.name: placeholder.text_value or placeholder.image_value for placeholder in placeholders}
    context['navbar_pages'] = navbar_pages
    template = os.path.join(settings.TEMPLATE_DIR,page.template_name)
    # Render the template dynamically based on the `Page` model's template_name
    return render(request, template, context)

def dynamic_page(request, slug):
    page = get_object_or_404(Page, slug=slug)
    placeholders = Placeholder.objects.filter(page=page)

    navbar_pages = Page.objects.filter(show_in_navbar=True)

    # Build a context with placeholders
    context = {placeholder.name: placeholder.text_value or placeholder.image_value for placeholder in placeholders}
    context['navbar_pages'] = navbar_pages
    template = os.path.join(settings.TEMPLATE_DIR,page.template_name)

    return render(request, template, context)




@csrf_exempt  # Ensure CSRF is handled properly in production
def add_page(request):
    if request.method == 'POST':
        form = PageForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return JsonResponse({'success': True, 'message': 'Page added successfully'})
        else:
            return JsonResponse({'success': False, 'errors': form.errors}, status=400)
    return JsonResponse({'success': False, 'errors': 'Invalid request'}, status=400)

def list_templates(request):
    # Assuming templates are in the 'templates/' directory at the root of the project
    templates = [f for f in os.listdir(settings.TEMPLATE_DIR) if os.path.isfile(os.path.join(settings.TEMPLATE_DIR, f)) and f.endswith('.html')]
    return JsonResponse({'templates': templates})


def get_placeholders(request):
    template_name = request.GET.get('template', '')
    if not template_name:
        return JsonResponse({'error': 'No template specified'}, status=400)

    template_path = os.path.join(settings.TEMPLATE_DIR, template_name)

    if not os.path.exists(template_path):
        return JsonResponse({'error': 'Template not found'}, status=404)

    # Read the template file
    with open(template_path, 'r') as file:
        content = file.read()

    # Extract placeholders from the template
    placeholders = {
        # You can use regex or any other method to find placeholders
        # For simplicity, assume placeholders are enclosed in {{ }} 
        # and are just variable names
        name.strip() 
        for name in re.findall(r'{{\s*(\w+)\s*}}', content)
    }

    return JsonResponse({'placeholders': list(placeholders)})

def list_pages(request):
    pages = Page.objects.all().values('id', 'title')
    return JsonResponse({'pages': list(pages)})

def generate_placeholders_html(template_name, page):
    template_path = os.path.join(settings.TEMPLATE_DIR, template_name)

    if not os.path.exists(template_path):
        return ''

    with open(template_path, 'r') as template_file:
        template_content = template_file.read()

    # Extract placeholders from the template content
    placeholders = extract_placeholders(template_content)

    # Get the existing placeholders from the database for the given page
    page_placeholders = Placeholder.objects.filter(page=page)
    placeholders_dict = {p.name: (p.text_value or p.image_value) for p in page_placeholders}

    placeholders_html = ''
    for key, label in placeholders.items():
        # Pre-populate text values if available
        if 'text' in key:
            text_value = placeholders_dict.get(key, '')  # Get existing value or empty string
            placeholders_html += f'''
                <div class="mb-3">
                    <label for="{key}" class="form-label">{label}:</label>
                    <textarea id="{key}" name="{key}" class="form-control" rows="4" placeholder="Enter {label.lower()} here">{text_value}</textarea>
                </div>'''
        # Pre-populate file inputs if available (e.g., images or icons)
        elif 'image' in key or 'icon' in key:
            image_value = placeholders_dict.get(key, None)  # Get existing image or None
            if image_value:
                image_preview = f'<img src="{image_value.url}" alt="{label}" class="img-thumbnail mb-2" style="max-height: 150px;">'
            else:
                image_preview = ''
            placeholders_html += f'''
                <div class="mb-3">
                    <label for="{key}" class="form-label">{label}:</label>
                    {image_preview}
                    <input type="file" id="{key}" name="{key}" class="form-control" accept="placeholders/*">
                </div>'''

    return placeholders_html



def extract_placeholders(template_content):
    placeholders = {}
    
    # Find placeholders enclosed in {{ }}
    matches = re.findall(r'\{\{\s*(\w+)(?:\.\w+)?\s*\}\}', template_content)
    for match in matches:
        key = match.strip()
        if key:  # Ignore empty matches
            placeholders[key] = key.replace('_', ' ').title()
    return placeholders



def get_page_data(request):
    page_id = request.GET.get('id')
    page = get_object_or_404(Page, id=page_id)

    # Pass both template_name and page to generate_placeholders_html
    placeholders_html = generate_placeholders_html(page.template_name, page)

    if placeholders_html:
        return JsonResponse({
            'success': True,
            'template_name': page.template_name,
            'placeholders_html': placeholders_html,
            'show_in_navbar': page.show_in_navbar  
      })
    else:
        return JsonResponse({'success': False, 'message': 'No placeholders found.'})


def update_placeholders(request, page_id):
    page = get_object_or_404(Page, id=page_id)
    errors = {}

    if request.method == 'POST':
        # Update navbar status
        show_in_navbar = request.POST.get('show_in_navbar') == 'on'
        page.show_in_navbar = show_in_navbar
        page.save()
        # Process POST data
        for key, value in request.POST.items():
            if key == 'csrfmiddlewaretoken':
                continue  # Skip CSRF token

            # Check if the placeholder exists or create it
            placeholder, created = Placeholder.objects.get_or_create(page=page, name=key)

            # Update text value if available
            if value and value.strip() != '':
                placeholder.text_value = value
                try:
                    placeholder.save()
                except Exception as e:
                    errors[key] = str(e)
        # Process file uploads from request.FILES
        for key, file in request.FILES.items():
            if file and file.size > 0:
                # Ensure the placeholder exists
                placeholder, created = Placeholder.objects.get_or_create(page=page, name=key)
                placeholder.image_value = file
                try:
                    placeholder.save()
                except Exception as e:
                    errors[key] = str(e)


        if errors:
            return JsonResponse({'success': False, 'errors': errors})

        return JsonResponse({'success': True, 'message': 'Placeholders updated successfully!'})

    return JsonResponse({'success': False, 'message': 'Invalid request method.'})






# View to edit a template
def edit_template(request, template_name):
    template_path = os.path.join(settings.TEMPLATE_DIR, template_name)

    if request.method == 'GET':
        if os.path.exists(template_path):
            with open(template_path, 'r') as file:
                content = file.read()
            return JsonResponse({'template_name': template_name, 'content': content})
        else:
            return JsonResponse({'error': 'Template not found'}, status=404)

    elif request.method == 'POST':
        new_content = request.POST.get('template_content', '')  # Ensure key matches form field name
        if new_content:
            try:
                with open(template_path, 'w') as file:
                    file.write(new_content)
                return JsonResponse({'success': True, 'message': 'Template updated successfully!'})
            except Exception as e:
                return JsonResponse({'success': False, 'message': f'Error saving template: {str(e)}'})
        else:
            return JsonResponse({'success': False, 'message': 'No content provided.'})



def add_template(request):
    if request.method == 'POST':
        template_name = request.POST.get('template_name')
        template_title = "{{ title_text }}"  # Get the new template title
        content = request.POST.get('template_content')  # Changed from 'content' to 'template_content'

        # Define path to the new template
        template_path = os.path.join(settings.TEMPLATE_DIR, f"{template_name}.html")

        # Check if any required fields are empty
        if not template_name or not template_title or not content:
            return JsonResponse({'success': False, 'message': 'Template name, title, or content is missing.'})

        # Add the extends, block title, and block content structure
        full_content = (
            "{% extends 'base/basePages.html' %}\n"
            "{% block title %}\n"
            f"{template_title}\n"  # Insert template title here
            "{% endblock %}\n\n"
            "{% block content %}\n\n"
            f"{content}\n\n"
            "{% endblock %}"
        )

        try:
            # Write the full content to the new template
            with open(template_path, 'w') as template_file:
                template_file.write(full_content)
            return JsonResponse({'success': True, 'message': 'Template added successfully!'})
        
        except IOError as e:
            # Handle IO errors (e.g., permission issues)
            return JsonResponse({'success': False, 'message': f'Error writing template: {str(e)}'})
    
    return JsonResponse({'error': 'Invalid request method.'}, status=400)




def get_template_content(request):
    template_name = request.GET.get('template_name')
    
    if not template_name:
        return JsonResponse({'error': 'No template name provided.'}, status=400)

    try:
        # Assuming your templates are stored in the templates/ directory
        template_path = os.path.join(settings.TEMPLATE_DIR, template_name)
        
        # Load the template content
        with open(template_path, 'r') as file:
            template_content = file.read()

        return JsonResponse({
            'template_name': template_name,
            'template_content': template_content
        })
    
    except FileNotFoundError:
        return JsonResponse({'error': 'Template not found.'}, status=404)
    except TemplateDoesNotExist:
        return JsonResponse({'error': 'Template does not exist.'}, status=404)