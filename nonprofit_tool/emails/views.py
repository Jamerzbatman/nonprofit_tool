from app_management.utils import log_error
import os
from django.shortcuts import render


## start new
def new(request):
    try:
        print("5")
    except Exception as e:
        log_error('5', 'new', str(e))
## end new

## start new 1
def new_1(request):
    try:
        print("5")
    except Exception as e:
        log_error('5', 'new_1', str(e))
## end new 1
