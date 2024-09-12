from .forms import WebSiteForm
from django.http import JsonResponse
from .models import WebSite, Tag, Log
from .forms import WebSiteForm
from django.db.models import Exists, OuterRef, BooleanField


def list_logs(request, website_id):
    # Filter logs to include only unresolved ones
    logs = Log.objects.filter(website_relation_id=website_id, resolved=False).values('id', 'message', 'type', 'timestamp', 'traceback', 'resolved')
    
    return JsonResponse({'logs': list(logs)})

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