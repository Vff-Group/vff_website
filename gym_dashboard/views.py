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
import os
from django.conf import settings
from django.http import JsonResponse

from PIL import Image  # Pillow library for image processing
# Create your views here.
serverToken="AAAApZY1ur0:APA91bHsk-e3OC5R2vqO7dD0WZp7ifULNzqrUPnQu07et7RLFMWWcwOqY9Bl-9YQWkuXUP5nM7bVMgMP-qKISf9Jcf2ix9j7oOkScq9-3BH0hfCH3nIWgkn4hbnmSLyw4pmq66rMZz8R"

#Login Page
@never_cache
def login_view(request):
    print("Login View is being called")
    alert_message = None
    # if request.method == "POST":
    #     username = request.POST.get('uname')
    #     password = request.POST.get('passwrd')
    #     query = "select usrname,username,password,usertbl.usrid,mobile_no,address,lat,lng,token,created_date from vff.admintbl,vff.usertbl where usertbl.usrid=admintbl.usrid and status='1' and username='"+str(username)+"' and password='"+str(password)+"'"
    #     user_data = execute_raw_query_fetch_one(query)
    #     if user_data and user_data[2]:
    #             # User is authorized
    #             print('User is Authorized')
    #             request.session['usrname'] = user_data[0]
    #             request.session['username'] = user_data[1]
    #             request.session['password'] = user_data[2]
    #             request.session['userid'] = user_data[3]
    #             request.session['notification_token'] = user_data[8]
    #             request.session['is_logged_in'] = True
    #             # Setting the session to expire after one day (86400 seconds)
    #             request.session.set_expiry(43400)
    #             print('All Session Data Saved') 
    #             return redirect('dashboard_app:all_branches')
    #     else:
    #         context = {
    #             'username': username,
    #             'password': password,
    #             'error_message': 'Invalid credentials please try again',  # You can customize this error message
    #             }
    #         return render(request, 'admin_pages_gym/login.html', context)
        
    return render(request,"admin_pages_gym/gym_login.html")

@never_cache
def select_branch(request):
    
    alert_message = None
    # if request.method == "POST":
    #     username = request.POST.get('uname')
    #     password = request.POST.get('passwrd')
    #     query = "select usrname,username,password,usertbl.usrid,mobile_no,address,lat,lng,token,created_date from vff.admintbl,vff.usertbl where usertbl.usrid=admintbl.usrid and status='1' and username='"+str(username)+"' and password='"+str(password)+"'"
    #     user_data = execute_raw_query_fetch_one(query)
    #     if user_data and user_data[2]:
    #             # User is authorized
    #             print('User is Authorized')
    #             request.session['usrname'] = user_data[0]
    #             request.session['username'] = user_data[1]
    #             request.session['password'] = user_data[2]
    #             request.session['userid'] = user_data[3]
    #             request.session['notification_token'] = user_data[8]
    #             request.session['is_logged_in'] = True
    #             # Setting the session to expire after one day (86400 seconds)
    #             request.session.set_expiry(43400)
    #             print('All Session Data Saved') 
    #             return redirect('dashboard_app:all_branches')
    #     else:
    #         context = {
    #             'username': username,
    #             'password': password,
    #             'error_message': 'Invalid credentials please try again',  # You can customize this error message
    #             }
    #         return render(request, 'admin_pages_gym/login.html', context)
        
    return render(request,"admin_pages_gym/gym_branch.html")

def dashboard_view(request):
    error_msg = 'No Data Found'
    current_url = request.get_full_path()
    # using the 'current_url' variable to determine the active card.
    context = {'current_url': current_url,'error_msg':error_msg}
    return render(request,"admin_pages_gym/dashboard.html",context)

def all_gym_members(request):
    error_msg = 'No Members Found'
    current_url = request.get_full_path()
    # using the 'current_url' variable to determine the active card.
    context = {'current_url': current_url,'error_msg':error_msg}
    return render(request,"gym_customer_pages/all_gym_members.html",context)

def add_new_gym_member(request):
    error_msg = 'No Members Found'
    current_url = request.get_full_path()
    # using the 'current_url' variable to determine the active card.
    context = {'current_url': current_url,'error_msg':error_msg}
    return render(request,"gym_customer_pages/add_new_member.html",context)












def epochToDateTime(epoch):
    datetime_obj = datetime.utcfromtimestamp(epoch)
    gmt_plus_0530 = pytz.timezone('Asia/Kolkata')
    datetime_obj_gmt_plus_0530 = datetime_obj.replace(tzinfo=pytz.utc).astimezone(gmt_plus_0530)
    deliveryEpoch = datetime_obj_gmt_plus_0530.strftime('%Y-%m-%d %I:%M:%S %p')
    return deliveryEpoch

def upload_images2(uploaded_image):
    # Generate a unique identifier for the image
    unique_identifier = str(uuid.uuid4())

    # Extract the file extension from the uploaded image
    file_extension = mimetypes.guess_extension(uploaded_image.content_type)

    # Construct the custom image name with the unique identifier and original extension
    custom_image_name = f'img_{unique_identifier}{file_extension}'
    # Assuming you have a MEDIA_ROOT where the images will be stored
    file_path = os.path.join(settings.MEDIA_ROOT, custom_image_name)

    # Open the uploaded image using Pillow
    img = Image.open(uploaded_image)
    img_resized = img.resize((300, 300))
    # Save the resized image
    img_resized.save(file_path)

    # Assuming you have a MEDIA_URL configured
    image_url = os.path.join(settings.MEDIA_URL, custom_image_name)
    print(f'Uploaded Image URL: {image_url}')
    return image_url


def execute_raw_query_fetch_one(query, params=None,):
    
    result = []
    try:
        print(f"{Fore.GREEN}Query Executed: {query}{Style.RESET_ALL}")
        with connection.cursor() as cursor:
            cursor.execute(query, params)
            result = cursor.fetchone()
            print(f"Result: {result}")
        return result
    except DatabaseError as e:
        print(f"{Fore.RED}DatabaseError Found: {e}{Style.RESET_ALL}")
        # Need To Handle the error appropriately, such as logging or raising a custom exception
        # roll back transactions if needed
        
        return 500
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        # Handle other unexpected errors
        return 500
    finally:
        # Ensure the cursor is closed to release resources
        cursor.close()  # Note: cursor might not be defined if an exception occurs earlier

def execute_raw_query(query, params=None,):
    
    result = []
    try:
        print(f"{Fore.GREEN}Query Executed: {query}{Style.RESET_ALL}")
        with connection.cursor() as cursor:
            cursor.execute(query, params)
            result = cursor.fetchall()
            print(f"Result: {result}, Result length: {len(result)}")
        return result
    except DatabaseError as e:
        print(f"{Fore.RED}DatabaseError Found: {e}{Style.RESET_ALL}")
        # Need To Handle the error appropriately, such as logging or raising a custom exception
        # roll back transactions if needed
        
        return 500
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        # Handle other unexpected errors
        return 500
    finally:
        # Ensure the cursor is closed to release resources
        cursor.close()  # Note: cursor might not be defined if an exception occurs earlier
