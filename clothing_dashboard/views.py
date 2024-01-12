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


# Create your views here.
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
    #         return render(request, 'admin_pages/login.html', context)
        
    return render(request,"admin_pages_clothing/login.html")

def dashboard_view(request):
    error_msg = 'No Data Found'
    current_url = request.get_full_path()
    # using the 'current_url' variable to determine the active card.
    context = {'current_url': current_url,'error_msg':error_msg}
    return render(request,"admin_pages_clothing/dashboard.html",context)

def all_customers(request):
    error_msg = 'No Customers Found'
    current_url = request.get_full_path()
    # using the 'current_url' variable to determine the active card.
    context = {'current_url': current_url,'error_msg':error_msg}
    return render(request,"customers/all_customer.html",context)

def all_main_categories(request):
    error_msg = 'No Main Categories Found'
    query = "select main_cat_id,main_title_name,status,images from vff.united_armor_main_categorytbl order by time_at DESC"
    
    query_result = execute_raw_query(query)
    
    
        
    data = []    
    if not query_result == 500:
        for row in query_result:
            
            data.append({
                'main_cat_id': row[0],
                'main_title_name': row[1],
                'status': row[2],
                'images': row[3],
                
               
            })
    else:
        error_msg = 'Something Went Wrong'
    current_url = request.get_full_path()
    # using the 'current_url' variable to determine the active card.
    context = {'query_result':data,'current_url': current_url,'error_msg':error_msg}
    return render(request,"categories/all_main_categories.html",context)

def all_categories(request,main_cat_id,main_cat_name):
    error_msg = 'No Category Found'
    query = "select catid,cat_name,active_status from vff.united_armor_categorytbl where main_catid='"+str(main_cat_id)+"' ORDER BY time_while_creation desc"
    
    query_result = execute_raw_query(query)
    
    
        
    data = []    
    if not query_result == 500:
        for row in query_result:
            
            data.append({
                'catid': row[0],
                'cat_name': row[1],
                'active_status': row[2],
                
                
               
            })
    else:
        error_msg = 'Something Went Wrong'
    current_url = request.get_full_path()
    # using the 'current_url' variable to determine the active card.
    context = {'query_result':data,'current_url': current_url,'error_msg':error_msg,'main_cat_id':main_cat_id,'main_cat_name':main_cat_name}
    return render(request,"categories/all_categories.html",context)

def all_sub_categories(request,main_cat_id,main_cat_name,cat_id,cat_name):
    error_msg = 'No Sub Category Found'
    query = "select sub_catid,sub_cat_name,time_creation from vff.united_armor_sub_categorytbl where catid='"+str(cat_id)+"'"
    
    query_result = execute_raw_query(query)
    
    
        
    data = []    
    if not query_result == 500:
        for row in query_result:
            
            data.append({
                'sub_catid': row[0],
                'sub_cat_name': row[1],
                'time_creation': row[2],
                
                
               
            })
    else:
        error_msg = 'Something Went Wrong'
    current_url = request.get_full_path()
    # using the 'current_url' variable to determine the active card.
    context = {'query_result':data,'current_url': current_url,'error_msg':error_msg,'main_cat_id':main_cat_id,'main_cat_name':main_cat_name,'cat_id':cat_id,'cat_name':cat_name}
    return render(request,"categories/all_sub_categories.html",context)


def all_products_details(request,main_cat_id,cat_id,sub_cat_id): 
    error_msg = 'No Products Found'
    query = "select productid,product_name,max_checkout_qty,price,offer_price,default_images from vff.united_armor_all_productstbl  where sub_catid='"+str(sub_cat_id)+"'"
    
    query_result = execute_raw_query(query)
    
    
        
    data = []    
    if not query_result == 500:
        for row in query_result:
            
            data.append({
                'productid': row[0],
                'product_name': row[1],
                'max_checkout_qty': row[2],
                'price': row[3],
                'offer_price': row[4],
                'default_images': row[5],
                
                
               
            })
    else:
        error_msg = 'Something Went Wrong'
    current_url = request.get_full_path()
    # using the 'current_url' variable to determine the active card.
    context = {'query_result':data,'current_url': current_url,'error_msg':error_msg,'main_cat_id':main_cat_id,'cat_id':cat_id,'sub_cat_id':sub_cat_id}
    return render(request,"all_products/all_products.html",context)

def add_new_product(request):
    return render(request,"all_products/add_new_product.html")

def add_new_main_category(request):
    
    error_msg = 'No Main Category Details Found'
    if request.method == "POST":
        main_category_name = request.POST.get('main_category_name')
        
        uploaded_image = request.FILES.get('category_image')
        
       

        # image_url='NA'
        if uploaded_image:
            image_url = upload_images2(uploaded_image)
        

        try:
            with connection.cursor() as cursor:
                update_query="insert into vff.united_armor_main_categorytbl (main_title_name,images) values ('"+str(main_category_name)+"','"+str(image_url)+"')"
                cursor.execute(update_query)
                connection.commit()
                print(f" Main Category {main_category_name} Inserted Successfully.")
                return redirect('clothing_dashboard_app:all_main_categories')
        except Exception as e:
            print(f"Error loading data: {e}")
            
    current_url = request.get_full_path()
    # using the 'current_url' variable to determine the active card.
    context = {'current_url': current_url,'error_msg':error_msg}
    return render(request,"categories/all_main_categories.html",context)
    
def update_main_category_details(request):
    
    error_msg = 'No Main Category Details Found'
    if request.method == "POST":
        main_category_name = request.POST.get('main_category_name')
        main_cat_id = request.POST.get('category_id')#Hidden Input Field
        uploaded_image = request.FILES.get('category_image')
        
        query = "select main_cat_id,main_title_name,status,images from vff.united_armor_main_categorytbl where main_cat_id='"+str(main_cat_id)+"'"
        user_data = execute_raw_query_fetch_one(query)
        if user_data:
            image_url = user_data[3]

        # image_url='NA'
        if uploaded_image:
            image_url = upload_images2(uploaded_image)
        

        try:
            with connection.cursor() as cursor:
                update_query="update vff.united_armor_main_categorytbl set main_title_name='"+str(main_category_name)+"',images='"+str(image_url)+"',time_at = EXTRACT(EPOCH FROM CURRENT_TIMESTAMP) where main_cat_id='"+str(main_cat_id)+"'"
                cursor.execute(update_query)
                connection.commit()
                print(f" Main Category {main_category_name} Updated Successfully.")
                return redirect('clothing_dashboard_app:all_main_categories')
        except Exception as e:
            print(f"Error loading data: {e}")
            
    current_url = request.get_full_path()
    # using the 'current_url' variable to determine the active card.
    context = {'current_url': current_url,'error_msg':error_msg}
    return render(request,"categories/all_main_categories.html",context)

def add_new_category(request):
    
    error_msg = 'No Category Details Found'
    if request.method == "POST":
        main_category_id = request.POST.get('main_category_id')
        main_category_name = request.POST.get('main_category_name')
        category_name = request.POST.get('category_name')
        
        

        try:
            with connection.cursor() as cursor:
                insert_query="insert into vff.united_armor_categorytbl (cat_name,main_catid) values ('"+str(category_name)+"','"+str(main_category_id)+"')"
                cursor.execute(insert_query)
                connection.commit()
                print(f" New Category {category_name} Inserted Successfully.")
                return redirect(reverse('clothing_dashboard_app:all_categories', kwargs={'main_cat_id': main_category_id,'main_cat_name':main_category_name}))
        except Exception as e:
            print(f"Error loading data: {e}")
            
    current_url = request.get_full_path()
    # using the 'current_url' variable to determine the active card.
    context = {'current_url': current_url,'error_msg':error_msg}
    return render(request,"categories/all_main_categories.html",context)

def update_category_details(request):
    
    error_msg = 'No  Category Details Found'
    if request.method == "POST":
        main_category_id = request.POST.get('main_category_id')
        main_category_name = request.POST.get('main_category_name')
        category_id = request.POST.get('category_id')
        category_name = request.POST.get('category_name')
        
        
        try:
            with connection.cursor() as cursor:
                update_query="update vff.united_armor_categorytbl set cat_name='"+str(category_name)+"',time_while_creation= EXTRACT(EPOCH FROM CURRENT_TIMESTAMP) where catid='"+str(category_id)+"'"
                cursor.execute(update_query)
                connection.commit()
                print(f" New Category {category_name} Updated Successfully.")
                return redirect(reverse('clothing_dashboard_app:all_categories', kwargs={'main_cat_id': main_category_id,'main_cat_name':main_category_name}))
        except Exception as e:
            print(f"Error loading data: {e}")
            
    current_url = request.get_full_path()
    # using the 'current_url' variable to determine the active card.
    context = {'current_url': current_url,'error_msg':error_msg}
    return render(request,"categories/all_categories.html",context)

def add_new_sub_category(request):
    
    error_msg = 'No Category Details Found'
    if request.method == "POST":
        main_category_id = request.POST.get('main_category_id')
        main_category_name = request.POST.get('main_category_name')
        category_name = request.POST.get('category_name')
        category_id = request.POST.get('category_id')
        sub_category_name = request.POST.get('sub_category_name')
        
        

        try:
            with connection.cursor() as cursor:
                insert_query="insert into vff.united_armor_sub_categorytbl (sub_cat_name,cat_id) values ('"+str(sub_category_name)+"','"+str(category_id)+"')"
                cursor.execute(insert_query)
                connection.commit()
                print(f" New Sub Category {sub_category_name} Inserted Successfully.")
                return redirect(reverse('clothing_dashboard_app:all_sub_categories', kwargs={'main_cat_id': main_category_id,'main_cat_name':main_category_name,'cat_id':category_id,'cat_name':category_name}))
        except Exception as e:
            print(f"Error loading data: {e}")
            
    current_url = request.get_full_path()
    # using the 'current_url' variable to determine the active card.
    context = {'current_url': current_url,'error_msg':error_msg}
    return render(request,"categories/all_main_categories.html",context)


def update_sub_category_details(request):
    
    error_msg = 'No Sub Category Details Found'
    if request.method == "POST":
        main_category_id = request.POST.get('main_category_id')
        main_category_name = request.POST.get('main_category_name')
        category_name = request.POST.get('category_name')
        category_id = request.POST.get('category_id')
        sub_category_name = request.POST.get('sub_category_name')
        
        

        try:
            with connection.cursor() as cursor:
                update_query="update vff.united_armor_sub_categorytbl set sub_cat_name='"+str(sub_category_name)+"',time_creation= EXTRACT (EPOCH FROM CURRENT_TIMESTAMP) where sub_catid=''"
                cursor.execute(update_query)
                connection.commit()
                print(f" Sub Category {sub_category_name} Updated Successfully.")
                return redirect(reverse('clothing_dashboard_app:all_sub_categories', kwargs={'main_cat_id': main_category_id,'main_cat_name':main_category_name,'cat_id':category_id,'cat_name':category_name}))
        except Exception as e:
            print(f"Error loading data: {e}")
            
    current_url = request.get_full_path()
    # using the 'current_url' variable to determine the active card.
    context = {'current_url': current_url,'error_msg':error_msg}
    return render(request,"categories/all_categories.html",context)
    
def all_purchase_orders(request):
    error_msg = 'No Purchase Order Created'
    current_url = request.get_full_path()
    context = {'current_url': current_url,'error_msg':error_msg}
    return render(request,"purchase_orders_pages/all_purchase_orders.html",context)

def add_new_purchase_orders(request):
    error_msg = 'No Purchase Order Created'
    current_url = request.get_full_path()
    context = {'current_url': current_url,'error_msg':error_msg}
    return render(request,"purchase_orders_pages/new_purchase_order.html",context)

def inventory(request):
    current_url = request.get_full_path()
    context = {'current_url': current_url}
    return render(request,"inventory_pages/dashboard_inventory.html",context)

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
