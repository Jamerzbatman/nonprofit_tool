import re
from app_management.utils import log_error
import os
from django.shortcuts import render


## start new
def new(request):
    try:
        print("fgsf")
    except Exception as e:
        log_error('5', 'new', str(e))
## end new

## start new 1
def new_1(request):
    try:
        print("os")
    except Exception as e:
        log_error('5', 'new_1', str(e))
## end new 1

## start new new

def new_new(request):
    try:
        print("bitch")
    except Exception as e:
        log_error('5', 'new_new', str(e))

## end new new
