from django.contrib.auth.decorators import login_required
from .forms import OrganizationForm
from .models import Organization
from django.http import JsonResponse


@login_required
def add_edit_organization(request):
    if request.method == 'POST':
        form = OrganizationForm(request.POST)
        if form.is_valid():
            # Check if the user already has an organization
            try:
                organization = Organization.objects.get(user=request.user)
                # Update existing organization
                form = OrganizationForm(request.POST, instance=organization)
                if form.is_valid():
                    form.save()
                    return JsonResponse({'success': True, 'message': 'Organization updated successfully'})
                else:
                    return JsonResponse({'success': False, 'errors': form.errors}, status=400)
            except Organization.DoesNotExist:
                # Create new organization if none exists
                organization = form.save(commit=False)
                organization.user = request.user
                organization.save()
                return JsonResponse({'success': True, 'message': 'Organization added successfully'})
        else:
            return JsonResponse({'success': False, 'errors': form.errors}, status=400)
    else:
        # Handle GET request: provide the existing organization or a new form
        try:
            organization = Organization.objects.get(user=request.user)
            form = OrganizationForm(instance=organization)
        except Organization.DoesNotExist:
            form = OrganizationForm()

