from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from pages.models import Page


@login_required
def dashboard_view(request):
    list_display = ('title', 'slug')
    prepopulated_fields = {'slug': ('title',)}
    # Check if the user is a superuser
    is_superuser = request.user.is_superuser

    # Choose the base template based on the user's superuser status
    is_super = True if is_superuser else False

    # Pass the base template to the context
    context = {
        'is_super': is_super,
        'list_display' : list_display,
        'prepopulated_fields' : prepopulated_fields
    }

    return render(request, 'dashboard/home.html', context)