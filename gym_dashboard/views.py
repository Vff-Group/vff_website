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
    request.session['branchid'] = ''
    alert_message = None
    if request.method == "POST":
        username = request.POST.get('uname')
        password = request.POST.get('passwrd')
        query = "select adminid,admin_name,usrid,gym_branchid from vff.gym_admintbl where username='"+str(username)+"' and password='"+str(password)+"'"
        user_data = execute_raw_query_fetch_one(query)
        if user_data and user_data[2]:
                # User is authorized
                print('User is Authorized')
                request.session['adminid'] = user_data[0]
                request.session['admin_name'] = user_data[1]
                request.session['gym_admin_userid'] = user_data[2]
                request.session['gym_branchid'] = user_data[3]
                
                request.session['is_gym_logged_in'] = True
                
                # Setting the session to expire after one day (86400 seconds)
                request.session.set_expiry(43400)
                print('All Session Data Saved') 
                return redirect('gym_dashboard_app:all_gym_branches')
        else:
            context = {
                'username': username,
                'password': password,
                'error_message': 'Invalid credentials please try again',  # You can customize this error message
                }
            return render(request, 'admin_pages_gym/gym_login.html', context)
        
    return render(request,"admin_pages_gym/gym_login.html")

@never_cache
def all_gym_branches(request):
    isLogin = is_loggedin(request)
    if isLogin == False:
        return redirect('gym_dashboard_app:login')
    print("All Branches Gym")
    error_msg = "No Branch Data Found"
    usrid = request.session.get('gym_admin_userid')
    request.session['branchid'] = ''
    
    query = "select gym_branch_id,gym_name,gym_branchtbl.created_date,gym_branchtbl.time_at,gym_branchtbl.address,usrid,adminid from vff.gym_admintbl,vff.gym_branchtbl where gym_branchtbl.gym_branch_id=gym_admintbl.gym_branchid and usrid='"+str(usrid)+"'"
    rows = execute_raw_query(query)
    data = []    
    if not rows == 500:
        for row in rows:
            data.append({
                'gym_branch_id': row[0],
                'gym_name': row[1],
                'created_date': row[2],
                'time_at': row[3],
                'address': row[4],
                'usrid': row[5],
                'adminid': row[6],
                
                
            })
    else:
        error_msg = 'Something Went Wrong. [Please Try after sometime ]'
    context = {'query_result': data,'error_msg':error_msg}
    return render(request,'admin_pages_gym/gym_branch.html',context)
        
#To save the selected branch ID and Name
def save_selected_gym_branch(request):
    if request.method == 'POST':
        gym_branch_id = request.POST.get('gym_branch_id')
        gym_name = request.POST.get('gym_name')
        address = request.POST.get('branch_address')
        admin_id = request.POST.get('branch_admin_id')
        
        
        
        request.session['gym_branch_id'] = gym_branch_id
        request.session['gym_name'] = gym_name
        request.session['gym_address'] = address
        request.session['gym_adminid'] = admin_id
        request.session['gym_branch_selected'] = True
        request.session.save()  # Save the session to persist the changes

        return redirect('gym_dashboard_app:dashboard')
    else:
        return redirect('gym_dashboard_app:all_gym_branches')    

def dashboard_view(request):
    isLogin = is_loggedin(request)
    if isLogin == False:
        return redirect('gym_dashboard_app:login')
    error_msg = 'No Data Found'
    gym_branchid = request.session.get('gym_branch_id')
    total_members = '0'
    #Total GYM Members
    query_members = "select count(*) from vff.gym_memberstbl where gymid='"+str(gym_branchid)+"'"
    result = execute_raw_query_fetch_one(query_members)
    if result:  
        total_members = result[0] 
        if total_members == None:
            total_members = '0'
            
    current_url = request.get_full_path()
    # using the 'current_url' variable to determine the active card.
    context = {'current_url': current_url,'error_msg':error_msg,'total_gym_members': total_members,}
    return render(request,"admin_pages_gym/dashboard.html",context)

def all_gym_members(request):
    isLogin = is_loggedin(request)
    if isLogin == False:
        return redirect('gym_dashboard_app:login')
    error_msg = 'No Members Found'
    gym_branch_id = request.session.get('gym_branch_id')
    query = "select memberid,name,email,mobno,date_of_birth,join_date,join_time,gender,weight,height,due_date,goal,profile_image from vff.gym_memberstbl where gymid='"+str(gym_branch_id)+"'"
    
    query_result = execute_raw_query(query)
    
    
        
    data = []    
    if not query_result == 500:
        for row in query_result:
            
            data.append({
                'memberid': row[0],
                'name': row[1],
                'email': row[2],
                'mobno': row[3],
                'date_of_birth': row[4],
                'join_date': row[5],
                'join_time': row[6],
                'gender': row[7],
                'weight': row[8],
                'height': row[9],
                'due_date': row[10],
                'goal': row[11],
                'profile_image': row[12],
            })
    else:
        error_msg = 'Something Went Wrong'
    current_url = request.get_full_path()
    # using the 'current_url' variable to determine the active card.
    context = {'query_result':data,'current_url': current_url,'error_msg':error_msg}
    
    return render(request,"gym_customer_pages/all_gym_members.html",context)

def add_new_gym_member(request):
    error_msg = 'No Members Found'
    if request.method == "POST":
        uname = request.POST.get('fullname')
        email_id = request.POST.get('email_id')
        primary_mobno = request.POST.get('primaryno')
        age = request.POST.get('age')
        password = request.POST.get('password')
        gender = request.POST.get('gender')
        address = request.POST.get('fulladdress')
        pin_code = request.POST.get('pincode')
        land_mark = request.POST.get('landmark')
        date_of_birth = request.POST.get('dateofbirth')
        date_of_joining = request.POST.get('dateofjoining')
        due_date = request.POST.get('duedate')
        uploaded_image = request.FILES.get('profile-image1')
        gym_branch_id = request.session.get('gym_branch_id')
        if uploaded_image:
            image_url = upload_images2(uploaded_image)
        else:
            # Handle the case where there's no uploaded image and no previous image
            image_url = 'https://t3.ftcdn.net/jpg/00/64/67/80/360_F_64678017_zUpiZFjj04cnLri7oADnyMH0XBYyQghG.jpg'  # Set it to a default value or handle accordingly
        try:
            with connection.cursor() as cursor:
                insert_query="insert into vff.gym_memberstbl (name,email,mobno,date_of_birth,join_date,gender,password,gymid,due_date,profile_image,address,pincode,landmark,age) values ('"+str(uname)+"','"+str(email_id)+"','"+str(primary_mobno)+"','"+str(date_of_birth)+"','"+str(date_of_joining)+"','"+str(gender)+"','"+str(password)+"','"+str(gym_branch_id)+"','"+str(due_date)+"','"+str(image_url)+"','"+str(address)+"','"+str(pin_code)+"','"+str(land_mark)+"','"+str(age)+"')"
                cursor.execute(insert_query)
                connection.commit()
                print("Member Added Successfully.")
                return redirect('gym_dashboard_app:all_gym_members')
        except Exception as e:
            print(f"Error loading data: {e}")
            
    current_url = request.get_full_path()
    # using the 'current_url' variable to determine the active card.
    context = {'current_url': current_url,'error_msg':error_msg}
    return render(request,"gym_customer_pages/add_new_member.html",context)

def update_gym_member(request,member_id):
    error_msg = 'No Members Found'
    current_url = request.get_full_path()
    data = {}
    if member_id:
        query = "select name,email,mobno,date_of_birth,join_date,gender,password,due_date,profile_image,address,pincode,landmark,age from vff.gym_memberstbl where memberid='"+str(member_id)+"'"
        result = execute_raw_query_fetch_one(query)
        if result:   
            data = {
                'fullname' : result[0],
                'email' : result[1],
                'primaryno' : result[2],
                'dateofbirth' : result[3],
                'dateofjoining' : result[4],
                'gender' : result[5],
                'password' : result[6],
                'due_date' : result[7],
                'profile_img' : result[8],
                'fulladdress' : result[9],
                'pincode' : result[10],
                'landmark' : result[11],
                'age' : result[12],
            }
       
            
    if request.method == "POST":
        uname = request.POST.get('fullname')
        email_id = request.POST.get('email_id')
        primary_mobno = request.POST.get('primaryno')
        age = request.POST.get('age')
        password = request.POST.get('password')
        gender = request.POST.get('gender')
        address = request.POST.get('fulladdress')
        pin_code = request.POST.get('pincode')
        land_mark = request.POST.get('landmark')
        date_of_birth = request.POST.get('dateofbirth')
        date_of_joining = request.POST.get('dateofjoining')
        due_date = request.POST.get('duedate')
        uploaded_image = request.FILES.get('profile-image1')
        gym_branch_id = request.session.get('gym_branch_id')
        if uploaded_image:
            image_url = upload_images2(uploaded_image)
        elif data.get('profile_img'):
            image_url = data.get('profile_img')
        else:
            # Handle the case where there's no uploaded image and no previous image
            image_url = 'https://t3.ftcdn.net/jpg/00/64/67/80/360_F_64678017_zUpiZFjj04cnLri7oADnyMH0XBYyQghG.jpg'  # Set it to a default value or handle accordingly
        try:
            with connection.cursor() as cursor:
                insert_query="update vff.gym_memberstbl set name='"+str(uname)+"',email='"+str(email_id)+"',mobno='"+str(primary_mobno)+"',date_of_birth='"+str(date_of_birth)+"',join_date='"+str(date_of_joining)+"',gender='"+str(gender)+"',password='"+str(password)+"',due_date='"+str(due_date)+"',profile_image='"+str(image_url)+"',address='"+str(address)+"',pincode='"+str(pin_code)+"',landmark='"+str(land_mark)+"',age='"+str(age)+"' where memberid='"+str(member_id)+"'"
                cursor.execute(insert_query)
                connection.commit()
                print("Member Updated Successfully.")
                return redirect('gym_dashboard_app:all_gym_members')
        except Exception as e:
            print(f"Error loading data: {e}")
            
    
    # using the 'current_url' variable to determine the active card.
    context = {'current_url': current_url,'error_msg':error_msg,'data':data}
    return render(request,"gym_customer_pages/add_new_member.html",context)

def all_fees_plans(request):
    isLogin = is_loggedin(request)
    if isLogin == False:
        return redirect('gym_dashboard_app:login')
    error_msg = 'No Fees Details Found'
    gym_branch_id = request.session.get('gym_branch_id')
    query = "select fdetail_id,fees_type,duration_in_months,price,description from vff.gym_fees_detailstbl where gym_id='"+str(gym_branch_id)+"'"
    
    query_result = execute_raw_query(query)
    
    
        
    data = []    
    if not query_result == 500:
        for row in query_result:
            
            data.append({
                'fdetail_id': row[0],
                'fees_type': row[1],
                'duration_in_months': row[2],
                'price': row[3],
                'description': row[4],
                
            })
    else:
        error_msg = 'Something Went Wrong'
    current_url = request.get_full_path()
    # using the 'current_url' variable to determine the active card.
    context = {'query_result':data,'current_url': current_url,'error_msg':error_msg}

    return render(request,"fees/all_fees_plans.html",context)


def add_new_fees_plan(request):
    
    error_msg = 'No Fees Details Found'
    if request.method == "POST":
        fees_type = request.POST.get('plan_name')
        duration_in_months = request.POST.get('duration_in_months')
        price = request.POST.get('plan_price')
        description = request.POST.get('plan_description')
        
        gym_branch_id = request.session.get('gym_branch_id')
        
        try:
            with connection.cursor() as cursor:
                insert_query="insert into vff.gym_fees_detailstbl(fees_type,duration_in_months,price,description,gym_id) values ('"+str(fees_type)+"','"+str(duration_in_months)+"','"+str(price)+"','"+str(description)+"','"+str(gym_branch_id)+"')"
                cursor.execute(insert_query)
                connection.commit()
                print("New Fees Plan Added Successfully.")
                return redirect('gym_dashboard_app:all_fees_plans')
        except Exception as e:
            print(f"Error loading data: {e}")
            
    current_url = request.get_full_path()
    # using the 'current_url' variable to determine the active card.
    context = {'current_url': current_url,'error_msg':error_msg}
    return render(request,"fees/all_fees_plans.html",context)
    

def update_fees_plan(request,fees_plan_id):
    
    error_msg = 'No Fees Details Found'
    if request.method == "POST":
        fees_type = request.POST.get('plan_name')
        duration_in_months = request.POST.get('duration_in_months')
        price = request.POST.get('plan_price')
        description = request.POST.get('plan_description')
        
        gym_branch_id = request.session.get('gym_branch_id')
        
        try:
            with connection.cursor() as cursor:
                insert_query="update vff.gym_fees_detailstbl set fees_type='"+str(fees_type)+"',duration_in_months='"+str(duration_in_months)+"',price='"+str(price)+"',description='"+str(description)+"' where fdetail_id='"+str(fees_plan_id)+"'"
                cursor.execute(insert_query)
                connection.commit()
                print(" Fees Plan Updated Successfully.")
                return redirect('gym_dashboard_app:all_fees_plans')
        except Exception as e:
            print(f"Error loading data: {e}")
            
    current_url = request.get_full_path()
    # using the 'current_url' variable to determine the active card.
    context = {'current_url': current_url,'error_msg':error_msg}
    return render(request,"fees/all_fees_plans.html",context)
    pass 










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
    custom_image_name = f'gym-member-{unique_identifier}{file_extension}'
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


def is_loggedin(request):
    # Check if the session variable 'is_logged_in' exists and is set to True
    print("checking if user has logged in or not")
    return request.session.get('is_gym_logged_in', False)