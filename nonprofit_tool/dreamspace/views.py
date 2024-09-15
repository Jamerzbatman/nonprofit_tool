from .forms import WebSiteForm
from django.http import JsonResponse
from .models import WebSite, Tag, Log, App, Function
from .forms import WebSiteForm, AppForm
from django.db.models import Exists, OuterRef, BooleanField
from django.shortcuts import get_object_or_404
import json


def list_logs(request, website_id):
    # Filter logs to include only unresolved ones
    logs = Log.objects.filter(website_relation_id=website_id, resolved=False).values('id', 'message', 'type', 'timestamp', 'traceback', 'resolved')
    
    return JsonResponse({'logs': list(logs)})

def list_app(request, website_id):
    # Ensure website exists
    app_website = WebSite.objects.filter(id=website_id).first()
    
    if not app_website:
        return JsonResponse({'error': 'WebSite not found'}, status=404)
    
    # Filter apps associated with the given website and are active
    error_subquery = Log.objects.filter(app_relation=OuterRef('pk'), resolved=False).values('pk')
    
    apps = App.objects.filter(
        website_relation=website_id,  # Filter apps associated with the website
        is_active=True  # Assuming you want to only include active apps
    ).annotate(
        has_error=Exists(error_subquery)
    ).order_by('-has_error', '-updated_at')

    # Format app names and include tags and error status
    app_data = [
        {
            'id': app.id,
            'name': app.name.replace('_', ' ').title(),
            'description': app.description,
            'active': app.is_active,
            'tags': [tag.name for tag in app.tags.all()],
            'error': app.has_error
        }
        for app in apps
    ]
        
    return JsonResponse({'apps': app_data})

def list_functions(request, app_id):
    # Ensure website exists
    function_app = App.objects.filter(id=app_id).first()

    
    if not function_app:
        return JsonResponse({'error': 'App not found'}, status=404)
    
    # Filter apps associated with the given website and are active
    error_subquery = Log.objects.filter(function_relation=OuterRef('pk'), resolved=False).values('pk')
    
    functions = Function.objects.filter(
        app_relation=app_id,  # Filter apps associated with the website
    ).annotate(
        has_error=Exists(error_subquery)
    ).order_by('-has_error', '-updated_at')

    # Format app names and include tags and error status
    function_data = [
        {
            'id': function.id,
            'name': function.name.replace('_', ' ').title(),
            'description': function.description,
            'tags': [tag.name for tag in app.tags.all()],
            'error': app.has_error
        }
        for function in functions
    ]
    app_name = function_app.name.replace('_', ' ').title()
    
    return JsonResponse({'functions': function_data, 'appName': app_name})



def list_global_apps(request, website_id):
    # Get the website instance
    try:
        website = WebSite.objects.get(id=website_id)
    except WebSite.DoesNotExist:
        return JsonResponse({'error': 'Website not found.'}, status=404)
    
    # Get global apps
    global_apps = App.objects.filter(is_global=True).exclude(website_relation=website)
    
    # Prepare data to send in the response
    apps_data = [{'id': app.id, 'name': app.name} for app in global_apps]
    
    return JsonResponse({'global_apps': apps_data})


def add_app_to_website(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        website_id = data.get('website_id')
        app_id = data.get('app_id')

        try:
            website = WebSite.objects.get(id=website_id)
            app = App.objects.get(id=app_id)

            # Add the website to the app's website_relation
            app.website_relation.add(website)
            return JsonResponse({'success': True})
        except (App.DoesNotExist, WebSite.DoesNotExist):
            return JsonResponse({'success': False, 'error': 'App or Website not found.'})

    return JsonResponse({'success': False, 'error': 'Invalid request.'})


def fetch_website(request, website_id):
    try:
        website = WebSite.objects.get(pk=website_id)
    except WebSite.DoesNotExist:
        return JsonResponse({'error': 'Website not found'}, status=404)
    
    # Manually construct the response data
    website_data = {
        'id': website.id,
        'name': website.name.replace('_', ' ').title(),
        'description': website.description,
        'created_at': website.created_at.isoformat(),
        'updated_at': website.updated_at.isoformat(),
        'is_active': website.is_active,
        'tags': [tag.name for tag in website.tags.all()]  # Assuming Tag model has a 'name' field
    }

    return JsonResponse(website_data)


def list_website(request):
    # Subquery to check for unresolved logs
    error_subquery = Log.objects.filter(website_relation=OuterRef('pk'), resolved=False).values('pk')

    # Annotate websites with an 'error' boolean field
    WebSites = WebSite.objects.annotate(
        has_error=Exists(error_subquery)
    ).order_by('-has_error', '-updated_at')

    # Format app names and include tags and error status
    formatted_WebSites = [
        {
            'id': WebSite.id,
            'name': WebSite.name.replace('_', ' ').title(),
            'description': WebSite.description,
            'active': WebSite.is_active,
            # Include the list of tag names
            'tags': [tag.name for tag in WebSite.tags.all()],
            # Include the error status
            'error': WebSite.has_error
        }
        for WebSite in WebSites
    ]

    return JsonResponse({'WebSite': formatted_WebSites})

def add_function_to_app(request):
    if request.method == 'POST':
            app_id = request.POST.get('appId')
            function_id = request.POST.get('funcitonId')
            function_name = request.POST.get('functionName', '').strip()
            function_description = request.POST.get('appDescription', '').strip()
            function_name = app_name.lower().replace(' ', '_')
            tags = request.POST.getlist('tags')
            if not function_name or not function_description:
                return JsonResponse({'success': False, 'error': 'App function and description are required'}, status=400)
            function = Function.objects.create(
                name=function_name,
                description=function_description,
                app_relation=app_id
            )
            tags_list = request.POST.getlist('tags')
            tags = []
            for tag_name in tags_list:
                tag_name = tag_name.strip()  # Remove any extra whitespace
                if tag_name:  # Ensure tag_name is not empty
                    tag, created = Tag.objects.get_or_create(name=tag_name)
                    tags.append(tag)
            
            # Associate tags with the App
            function.tags.set(tags)

            return JsonResponse({'success': True, 'function_id': function.id, 'app_id': app_id})


def add_app_to_dreamspace(request):
    if request.method == 'POST':
        website_id = request.POST.get('websiteId')
        app_name = request.POST.get('appName', '').strip()
        app_description = request.POST.get('appDescription', '').strip()
        # Format the app name
        app_name = app_name.lower().replace(' ', '_')
        
        tags = request.POST.getlist('tags')  # If tags are passed as a list of IDs or names
        
        # Check if app_name and app_description are not empty
        if not app_name or not app_description:
            return JsonResponse({'success': False, 'error': 'App name and description are required'}, status=400)
        
        # Create the App object
        app = App.objects.create(
            name=app_name,
            description=app_description
        )

        tags_list = request.POST.getlist('tags')
       # Handle tags
        tags = []
        for tag_name in tags_list:
            tag_name = tag_name.strip()  # Remove any extra whitespace
            if tag_name:  # Ensure tag_name is not empty
                tag, created = Tag.objects.get_or_create(name=tag_name)
                tags.append(tag)
        
        # Associate tags with the App
        app.tags.set(tags)
                  
        # Handle website_relation
        if website_id:
            try:
                website = get_object_or_404(WebSite, id=website_id)
                app.website_relation.add(website)
            except WebSite.DoesNotExist:
                return JsonResponse({'success': False, 'error': 'WebSite not found'}, status=404)
        
        return JsonResponse({'success': True, 'app_id': app.id, 'webSite_id': website_id})
    else:
        # Return form errors if the form is not valid
        return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=400)
    
        

def add_website(request):
    if request.method == 'POST':
        form = WebSiteForm(request.POST)
        if form.is_valid():
            # Save the website using form.save(), which returns the model instance
            new_website = form.save(commit=False)

            # Handle tags
            tags_list = form.cleaned_data.get('tags', [])
            
            # Create or get existing tags
            tags = []
            for tag_name in tags_list:
                tag, created = Tag.objects.get_or_create(name=tag_name)
                tags.append(tag)
            
            # Save the website to get the ID
            new_website.save()

            # Associate tags with the website
            new_website.tags.set(tags)

            try:
                # If your app creation logic succeeds, return success response
                return JsonResponse({'success': True, 'id': new_website.id, 'name': new_website.name.replace('_', ' ').title()})
            except Exception as e:
                # If the app creation fails, optionally delete the database entry
                new_website.delete()
                return JsonResponse({'success': False, 'error': str(e)})

        else:
            # Return form errors if the form is not valid
            return JsonResponse({'success': False, 'errors': form.errors})
    
    # Return an error for non-POST requests
    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=400)



def tag_autocomplete(request):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        term = request.GET.get('term', '')
        tags = Tag.objects.filter(name__icontains=term).values_list('name', flat=True)
        return JsonResponse({'tags': list(tags)})
    return JsonResponse({'tags': []}, status=400)