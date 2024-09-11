from .forms import WebSiteForm
from django.http import JsonResponse
from .models import WebSite, Tag
from .forms import WebSiteForm

def list_website(request):
    # Use prefetch_related to fetch tags efficiently
    WebSites = WebSite.objects.prefetch_related('tags').order_by('-updated_at')

    # Format app names and include tags
    formatted_WebSites = [
        {
            'id': WebSite.id,
            'name': WebSite.name.replace('_', ' ').title(),
            'description': WebSite.description,
            'active': WebSite.is_active,
            # Include the list of tag names
            'tags': [tag.name for tag in WebSite.tags.all()]
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