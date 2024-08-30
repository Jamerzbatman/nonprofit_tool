from app_management.utils import log_error
import os
from django.shortcuts import render

# Create your views here.




def testing_this_awesome_function(request):
    try:
        print("hotdog")
    except Exception as e:
        log_error('5', 'testing_this_awesome_function', str(e))
