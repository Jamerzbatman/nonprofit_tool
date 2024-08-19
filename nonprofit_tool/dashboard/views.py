from django.contrib.auth.decorators import login_required
from organization.forms import OrganizationForm
from django.shortcuts import render, redirect
from organization.models import Organization


@login_required
def dashboard_view(request):
    list_display = ('title', 'slug')
    prepopulated_fields = {'slug': ('title',)}

    # Check if the user is a superuser
    is_superuser = request.user.is_superuser

    # Check if the user already has an organization
    try:
        organization = Organization.objects.get(user=request.user)
        form = OrganizationForm(instance=organization)
    except Organization.DoesNotExist:
        form = OrganizationForm()

    # Choose the base template based on the user's superuser status
    is_super = True if is_superuser else False

    # Pass the base template and form to the context
    context = {
        'is_super': is_super,
        'list_display': list_display,
        'prepopulated_fields': prepopulated_fields,
        'OrganizationForm': form  # Pass the form instance to the context
    }

    return render(request, 'dashboard/home.html', context)