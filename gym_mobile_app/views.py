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
# Create your views here.

def login(request):
    if request.method == "POST":
        jdict = json.loads(request.body)
        print(f'jdict::{jdict}')
        mobno=jdict['mobno']
        emailid = jdict['email_id']
    return JsonResponse({'response':'Success','email_id':emailid,'mobno':mobno})