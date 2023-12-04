from django.shortcuts import render,redirect, reverse
from django.db import connection, DatabaseError
from django.views.decorators.cache import never_cache
from django.contrib.auth import logout
from django.http import HttpResponseServerError,JsonResponse,HttpResponse,HttpResponseRedirect
from colorama import Fore, Style
from django.views.decorators.cache import never_cache
from django.utils import timezone
from datetime import datetime
import pytz
import base64
import os
import uuid
import mimetypes
import requests
import json
import time
import re
from django.middleware.csrf import get_token
# Create your views here.

def login(request):
    if request.method == "POST":
        # Printing headers
        received_headers = request.headers
        print(f"Received Headers: {received_headers}")

        # Parsing and printing JSON body
        try:
            jdict = json.loads(request.body)
            print(f"Received Body: {jdict}")
            mobno = jdict['mobno']
            emailid = jdict['email_id']
            return JsonResponse({'response': 'Success', 'email_id': emailid, 'mobno': mobno})
        except json.JSONDecodeError as e:
            print(f"Failed to parse JSON: {e}")
            return JsonResponse({'error': 'Invalid JSON format'})

    return JsonResponse({'error': 'Something Went Wrong'})

def get_csrf_token(request):
    csrf_token = get_token(request)
    print(f'csrf_token_django::{csrf_token}')
    return JsonResponse({'csrf_token': csrf_token})