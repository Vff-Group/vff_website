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


from PIL import Image  # Pillow library for image processing
# Create your views here.
serverToken="AAAApZY1ur0:APA91bHsk-e3OC5R2vqO7dD0WZp7ifULNzqrUPnQu07et7RLFMWWcwOqY9Bl-9YQWkuXUP5nM7bVMgMP-qKISf9Jcf2ix9j7oOkScq9-3BH0hfCH3nIWgkn4hbnmSLyw4pmq66rMZz8R"

# Initialize Firebase Admin SDK
import firebase_admin
from firebase_admin import credentials, messaging

# cred = credentials.Certificate('path/to/serviceAccountKey.json')
# firebase_admin.initialize_app(cred)


# def sendFMCMsg(deviceToken,msg,title,data):
#     global serverToken
#     deviceToken=deviceToken.replace('__colon__',':')
#     headers = {
#         'Content-Type': 'application/json',
#         'Authorization': 'key=' + serverToken,
#     }
#     body = {
#         'notification': {'title': title,
#         'body': msg
#     },
#         'data': data,
#         'to':
#         deviceToken,
#         'priority': 'high',
# #   'data': dataPayLoad,
#     }
#     response = requests.post("https://fcm.googleapis.com/fcm/send",headers = headers, data=json.dumps(body))
#     print(response)
#     print(response.json())
#     print(response.status_code)

#To Register for Firebase Web Setup
def showFirebaseJS(request):
    
  data='importScripts("https://www.gstatic.com/firebasejs/10.5.0/firebase-app.js");' \
         'importScripts("https://www.gstatic.com/firebasejs/10.5.0/firebase-analytics.js"); ' \
# 'import { getMessaging, getToken } from "https://www.gstatic.com/firebasejs/10.5.0/firebase-messaging.js";'
  
  'var firebaseConfig = {'\
  '  apiKey: "AIzaSyB377d4_AFRtoEIjpN2Puf3CYwe-I9dCGE",'\
  '  authDomain: "vff-group-b185c.firebaseapp.com",'\
  '  projectId: "vff-group-b185c",'\
  '  storageBucket: "vff-group-b185c.appspot.com",'\
  '  messagingSenderId: "711189707453",'\
  '  appId: "1:711189707453:web:3813986a11e36f830b55d4",'\
  '  measurementId: "G-YYEJHD2GJ1"'\
  '};'\

  'firebase.initializeApp(firebaseConfig);' \
         'const messaging=firebase.messaging();' \
         'messaging.setBackgroundMessageHandler(function (payload) {' \
         '    console.log(payload);' \
         '    const notification=JSON.parse(payload);' \
         '    const notificationOption={' \
         '        body:notification.body,' \
         '        icon:notification.icon' \
         '    };' \
         '    return self.registration.showNotification(payload.notification.title,notificationOption);' \
         '});'
                
                              
  
  
  return HttpResponse(data,content_type="text/javascript")

def send(request):
    resgistration  = [
    ]
    send_notification(resgistration , 'Code Keen added a new video' , 'Code Keen new video alert')
    return HttpResponse("sent")
def send_notification(registration_ids , message_title , message_desc):
    fcm_api =serverToken
    url = "https://fcm.googleapis.com/fcm/send"
    
    headers = {
    "Content-Type":"application/json",
    "Authorization": 'key='+fcm_api}

    payload = {
        "registration_ids" :registration_ids,
        "priority" : "high",
        "notification" : {
            "body" : message_desc,
            "title" : message_title,
            "image" : "https://i.ytimg.com/vi/m5WUPHRgdOA/hqdefault.jpg?sqp=-oaymwEXCOADEI4CSFryq4qpAwkIARUAAIhCGAE=&rs=AOn4CLDwz-yjKEdwxvKjwMANGk5BedCOXQ",
            "icon": "https://yt3.ggpht.com/ytc/AKedOLSMvoy4DeAVkMSAuiuaBdIGKC7a5Ib75bKzKO3jHg=s900-c-k-c0x00ffffff-no-rj",
            
        }
    }

    result = requests.post(url,  data=json.dumps(payload), headers=headers )
    print(result.json())


def sendFMCMsg(deviceToken, msg, title, data):
    global serverToken
    deviceToken = deviceToken.replace('__colon__', ':')

    # Validate the device token
    if not deviceToken:
        print("Invalid device token")
        return

    # Check if the token has already been sent a notification
    # (You may want to implement a more robust solution to track notifications)

    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'key=' + serverToken,
    }

    body = {
        'notification': {
            'title': title,
            'body': msg
        },
        'data': data,
        'to': deviceToken,
        'priority': 'high',
    }

    try:
        response = requests.post("https://fcm.googleapis.com/fcm/send", headers=headers, data=json.dumps(body))
        response_data = response.json()
        print("FCM Response:")
        print(response_data)
        print("Status Code:", response.status_code)
    except requests.exceptions.RequestException as e:
        print("Error sending FCM notification:", e)

#Login Page
@never_cache
def login_view(request):
    print("Login View is being called")
    alert_message = None
    if request.method == "POST":
        username = request.POST.get('uname')
        password = request.POST.get('passwrd')
        query = "select usrname,username,password,usertbl.usrid,mobile_no,address,lat,lng,token,created_date from vff.admintbl,vff.usertbl where usertbl.usrid=admintbl.usrid and status='1' and username='"+str(username)+"' and password='"+str(password)+"'"
        user_data = execute_raw_query_fetch_one(query)
        if user_data and user_data[2]:
                # User is authorized
                print('User is Authorized')
                request.session['usrname'] = user_data[0]
                request.session['username'] = user_data[1]
                request.session['password'] = user_data[2]
                request.session['userid'] = user_data[3]
                request.session['notification_token'] = user_data[8]
                request.session['is_logged_in'] = True
                # Setting the session to expire after one day (86400 seconds)
                request.session.set_expiry(43400)
                print('All Session Data Saved') 
                return redirect('dashboard_app:all_branches')
        else:
            context = {
                'username': username,
                'password': password,
                'error_message': 'Invalid credentials please try again',  # You can customize this error message
                }
            return render(request, 'admin_pages/login.html', context)
        
    return render(request,"admin_pages/login.html",{'error_message': alert_message})

#All Branches
def all_branches(request):
    print("All Branches")
    error_msg = "No Vendors Data Found"
    usrid = request.session.get('userid')
    request.session['branchid'] = ''
    print(f'Admin Usrid ::{usrid}')
    query = "select branchtbl.branchid,branch_name,branchtbl.address,branch_type,creation_date,branchtbl.status,gstno,igstno,branchtbl.city,state,branchtbl.pincode,usrname,admintbl.usrid,contactno,gstno from vff.usertbl,vff.branchtbl,vff.admintbl where admintbl.branchid=branchtbl.branchid and usertbl.usrid=admintbl.usrid and admintbl.usrid='"+str(usrid)+"'"
    rows = execute_raw_query(query)
    data = []    
    if not rows == 500:
        for row in rows:
            data.append({
                'branchid': row[0],
                'branch_name': row[1],
                'address': row[2],
                'branch_type': row[3],
                'creation_date': row[4],
                'status': row[5],
                'gstno': row[6],
                'igstno': row[7],
                'city': row[8],
                'state': row[9],
                'pincode': row[10],
                'admin_name': row[11],
                'admin_id': row[12],
                'contactno': row[13],
                'gstno': row[14],
                
            })
    else:
        error_msg = 'Something Went Wrong. [Please Try after sometime ]'
    context = {'query_result': data,'error_msg':error_msg}
    return render(request,'admin_pages/all_branches.html',context)

#To save the selected branch ID and Name
def save_selected_branch(request):
    if request.method == 'POST':
        branchid = request.POST.get('branchid')
        branch_name = request.POST.get('branch_name')
        branch_address = request.POST.get('branch_address')
        branch_gstno = request.POST.get('branch_gstno')
        branch_igstno = request.POST.get('branch_igstno')
        branch_city = request.POST.get('branch_city')
        branch_state = request.POST.get('branch_state')
        branch_pincode = request.POST.get('branch_pincode')
        branch_contactno = request.POST.get('branch_contactno')
        branch_admin_name = request.POST.get('branch_admin_name')
        branch_admin_id = request.POST.get('branch_admin_id')
        print(branch_name,branchid,branch_address)
        # Save the selected branchid and brandname to the session
        
        request.session['branchid'] = branchid
        request.session['branch_name'] = branch_name
        request.session['branch_address'] = branch_address
        request.session['branch_gstno'] = branch_gstno
        request.session['branch_igstno'] = branch_igstno
        request.session['branch_city'] = branch_city
        request.session['branch_state'] = branch_state
        request.session['branch_pincode'] = branch_pincode
        request.session['branch_contactno'] = branch_contactno
        request.session['branch_admin_name'] = branch_admin_name
        request.session['branch_admin_id'] = branch_admin_id
        request.session['branch_selected'] = True
        request.session.save()  # Save the session to persist the changes

        return redirect('dashboard_app:dashboard')
    else:
        return redirect('dashboard_app:all_branches')
    
def search_orderid_or_mobile_number(request):
    if request.method == "POST":
        searchid = request.POST.get("searchid")
        type = request.POST.get("type")
        print(f'Type of serach::{type}')
        if type == "Order ID":
            query = "select orderid from vff.laundry_ordertbl where orderid='"+str(searchid)+"'"
            result = execute_raw_query_fetch_one(query)
            if result:  
                orderid = result[0]
                # return redirect('dashboard_app:view_order_detail',orderid=orderid)
                return JsonResponse({'orderFound': True, 'orderid': orderid})
            else:
                return JsonResponse({'orderFound': False})
        elif type == "Mobile Number":
            
            # query = "select orderid from vff.laundry_ordertbl where orderid='"+str(searchid)+"'"
            query_mobno = "select orderid,usrname from vff.usertbl,vff.laundry_customertbl,vff.laundry_ordertbl where laundry_customertbl.consmrid=laundry_ordertbl.customerid and laundry_customertbl.usrid=usertbl.usrid and  mobile_no='"+str(searchid)+"' order by orderid desc limit 1"
            result_mobno = execute_raw_query_fetch_one(query_mobno)
            if result_mobno:  
                orderid = result_mobno[0]
                print(f'orderid::::{orderid}')
                # return redirect('dashboard_app:view_order_detail',orderid=orderid)
                return JsonResponse({'orderFound': True, 'orderid': orderid})
            else:
                return JsonResponse({'orderFound': False})
        else:
            return JsonResponse({'orderFound': False})
           

#Dashboard Page
def dashboard(request):
    print('admin Dashboard Welcome page')
    # Check if the session variable 'is_logged_in' exists and is set to True
    # if not request.session.get('is_logged_in', False):
    #     # User is not logged in, redirect to the login page
    #     return redirect('dashboard_app:login')
    isLogin = is_loggedin(request)
    if isLogin == False:
        return redirect('dashboard_app:login')
    
    branchid = request.session.get('branchid')
    filter=''
    delivery_filter=''
    order_filter=''
    total_money = '0'
    total_customers = '0'
    total_delivery_boys = '0'
    total_orders_delivered = '0'
    if branchid:
        filter = "where branch_id='"+str(branchid)+"'"
        delivery_filter = "where branchid='"+str(branchid)+"'"
        order_filter = " and branch_id='"+str(branchid)+"'"
    #Total Amount
    query_amount = "select sum(price) as total_cost from vff.laundry_ordertbl "+filter+""
    result = execute_raw_query_fetch_one(query_amount)
    if result:  
        total_money = result[0] 
        if total_money == None:
            total_money = '0'
    
    
    #Total Customers
    query_customers = "select count(*) from vff.laundry_customertbl "
    c_result = execute_raw_query_fetch_one(query_customers)
    if c_result:  
        total_customers = c_result[0] 
        
    #Total Delivery Boys
    query_delivery = "select count(*) from vff.laundry_delivery_boytbl  "+delivery_filter+""
    d_result = execute_raw_query_fetch_one(query_delivery)
    if d_result:  
        total_delivery_boys = d_result[0] 
    
    #Total Orders Delivered
    query_orders = "select count(*) from vff.laundry_ordertbl where order_completed='1' "+order_filter+""
    d_result = execute_raw_query_fetch_one(query_orders)
    if d_result:  
        total_orders_delivered = d_result[0] 
        
    
    current_url = request.get_full_path()
    # using the 'current_url' variable to determine the active card.
    context = {
        'current_url': current_url,
        'total_money': total_money,
        'total_customers':total_customers,
        'total_delivery_boys':total_delivery_boys,
        'total_orders_delivered':total_orders_delivered
    }
    return render(request, 'admin_pages/dashboard.html', context)

#All STaff Employee Details Page
def all_staff(request):
    isLogin = is_loggedin(request)
    if isLogin == False:
        return redirect('dashboard_app:login')
    error_msg = "No Employees Created Yet"
    branch_id = request.session.get('branchid')
    filter = ''
    if branch_id :
        filter = " and laundry_employeetbl.branchid='"+str(branch_id)+"'"
    query = " select laundry_employeetbl.usrid,usrname,mobile_no,usertbl.address,lat,lng,age,gender,laundry_employeetbl.branchid,emplyid,laundry_employeetbl.status,is_online,usertbl.epoch,profile_img from vff.laundry_employeetbl,vff.usertbl where laundry_employeetbl.usrid=usertbl.usrid "+filter+"  order by usrname desc"
    
    query_result = execute_raw_query(query)
    
    
        
    data = []    
    if not query_result == 500:
        for row in query_result:
            epoch_time = row[12]
            print(f'Epoch_time::{epoch_time}')
            datetime_obj = datetime.utcfromtimestamp(epoch_time)
            print(f'datetime_obj::{datetime_obj}')
            gmt_plus_0530 = pytz.timezone('Asia/Kolkata')
            datetime_obj_gmt_plus_0530 = datetime_obj.replace(tzinfo=pytz.utc).astimezone(gmt_plus_0530)
            formatted_datetime = datetime_obj_gmt_plus_0530.strftime('%Y-%m-%d %I:%M:%S %p')
            data.append({
                'usrid': row[0],
                'usrname': row[1],
                'mobno': row[2],
                'address': row[3],
                'lat': row[4],
                'lng': row[5],
                'age': row[6],
                'gender': row[7],
                'branchid': row[8],
                'emplyid': row[9],
                'active_status': row[10],
                'is_online': row[11],
                'branch_name': row[12],
                'creation_date_time':formatted_datetime,
                'profile_img': row[13],
               
            })
    else:
        error_msg = 'Something Went Wrong'
    current_url = request.get_full_path()
    # using the 'current_url' variable to determine the active card.
    context = {'query_result': data,'current_url': current_url,'error_msg':error_msg}
    
    return render(request, 'staff_pages/all_staff_members.html',context)
    
    
#All Customers Page
def all_customers(request):
    isLogin = is_loggedin(request)
    if isLogin == False:
        return redirect('dashboard_app:login')
    error_msg = "No Customers Data Found"
    branch_id = request.session.get('branchid')
    filter = ''
    # if branch_id :
    #     filter = " and laundry_customertbl.branchid='"+str(branch_id)+"'"
    query = " select laundry_customertbl.usrid,usrname,mobile_no,usertbl.address,lat,lng,age,gender,laundry_customertbl.branchid,consmrid,laundry_customertbl.status,is_online,usertbl.epoch,profile_img from vff.laundry_customertbl,vff.usertbl where laundry_customertbl.usrid=usertbl.usrid "+filter+"  order by usertbl.usrid desc"
    
    query_result = execute_raw_query(query)
    
    
        
    data = []    
    if not query_result == 500:
        for row in query_result:
            epoch_time = row[12]
            print(f'Epoch_time::{epoch_time}')
            datetime_obj = datetime.utcfromtimestamp(epoch_time)
            print(f'datetime_obj::{datetime_obj}')
            gmt_plus_0530 = pytz.timezone('Asia/Kolkata')
            datetime_obj_gmt_plus_0530 = datetime_obj.replace(tzinfo=pytz.utc).astimezone(gmt_plus_0530)
            formatted_datetime = datetime_obj_gmt_plus_0530.strftime('%Y-%m-%d %I:%M:%S %p')
            data.append({
                'usrid': row[0],
                'usrname': row[1],
                'mobno': row[2],
                'address': row[3],
                'lat': row[4],
                'lng': row[5],
                'age': row[6],
                'gender': row[7],
                'branchid': row[8],
                'customerid': row[9],
                'active_status': row[10],
                'is_online': row[11],
                'branch_name': row[12],
                'creation_date_time':formatted_datetime,
                'profile_img': row[13],
               
            })
    else:
        error_msg = 'Something Went Wrong'
    current_url = request.get_full_path()
    # using the 'current_url' variable to determine the active card.
    context = {'query_result': data,'current_url': current_url,'error_msg':error_msg}
    
    return render(request, 'customer_pages/all_customers.html',context)


#Add New Customer Page
def add_customer(request,usrid=None):
    
    isLogin = is_loggedin(request)
    if isLogin == False:
        return redirect('dashboard_app:login')
    # If usrid is provided, retrieve the data for the selected Customer
    data = {}
    print(usrid)
    if usrid:
        try:
            with connection.cursor() as cursor:
                cursor.execute("select usrname,mobile_no,usertbl.address,age,gender,consmrid,landmark,date_of_birth,pincode,query,profile_img,laundry_customertbl.branchid,gstno,company_name,igstno"
                               " from vff.laundry_customertbl,vff.usertbl where laundry_customertbl.usrid=usertbl.usrid and laundry_customertbl.usrid='"+str(usrid)+"'")
                row = cursor.fetchone()
                print(f'fetching the single user data::{row}')
                if row:
                    image_url = row[10]
                    data = {
                        'usrid': usrid,
                        'fullname': row[0],
                        'primaryno': row[1],
                        'fulladdress': row[2],
                        'age': row[3],
                        'gender': row[4],
                        'customerid': row[5],
                        'landmark': row[6],
                        'dateofbirth': row[7],
                        'pincode': row[8],
                        'questions': row[9],
                        'profile_img': image_url,
                        'branch_id': row[11],
                        'gstno': row[12],
                        'company_name': row[13],
                        'igstno': row[14],
                        
                    }
        except Exception as e:
            print(f"Error loading data: {e}") 
       
    if request.method == "POST":
        uname = request.POST.get('fullname')
        primary_mobno = request.POST.get('primaryno')
        age = request.POST.get('age')
        gender = request.POST.get('gender')
        address = request.POST.get('fulladdress')
        pincode = request.POST.get('pincode')
        land_mark = request.POST.get('landmark')
        date_of_birth = request.POST.get('dateofbirth')
        queries = request.POST.get('questions')
        gstno = request.POST.get('gstno')
        igstno = request.POST.get('igstno')
        company_name = request.POST.get('company_name')
        uploaded_image = request.FILES.get('profile-image1')

        
        if uploaded_image:
            image_url = upload_images2(uploaded_image)
        elif data.get('profile_img'):
            image_url = data.get('profile_img')
        else:
            # Handle the case where there's no uploaded image and no previous image
            image_url = 'NA'  # Set it to a default value or handle accordingly
            
        # image_url = 'NA'
        # if request.FILES.get('profile-image1'):
        #         uploaded_image = request.FILES['profile-image1']
        #         image_url = upload_images2(uploaded_image)
            

        
        
        if not queries:
            queries = 'No queries'
        if not gstno:
            gstno = "-1"
        if not igstno:
            igstno = "-1"
        if not company_name:
            company_name = "NA"
        errors = []
        if not date_of_birth:
            today_date = timezone.now().date() 
            formatted_date = today_date.strftime('%Y-%m-%d')
            date_of_birth = formatted_date
        if not age:
            age = '-1'
        if not land_mark:
            land_mark = 'NA'
        branch_id = request.session.get('branchid')
        print(f'branch_id:{branch_id}')
        # if not branch_id:
        #     # If there are validation errors, render the form with error messages
        #     errors = "Please select Branch ID to add new customer"
        #     return render(request,'customer_pages/add_customer.html',{'data':data,'error':errors})
        
        try:
            with connection.cursor() as cursor:
                if usrid:
                    # Update an existing customers
                    update_query = (
                        "update vff.usertbl set usrname='"+str(uname)+"',mobile_no='"+str(primary_mobno)+"',address='"+str(address)+"',age='"+str(age)+"',gender='"+str(gender)+"',date_of_birth='"+str(date_of_birth)+"',pincode='"+str(pincode)+"',landmark='"+str(land_mark)+"',profile_img='"+str(image_url)+"' where usrid='"+str(usrid)+"'"
                    )
                    print(f"update user details::{update_query}")
                    cursor.execute(update_query)
                    
                    update_customer = (
                        "update vff.laundry_customertbl set customer_name='"+str(uname)+"', query='"+str(queries)+"', gstno='"+str(gstno)+"', company_name='"+str(company_name)+"',igstno='"+str(igstno)+"' where usrid='"+str(usrid)+"'"
                    )
                    print(f"update customer details::{update_customer}")
                    cursor.execute(update_customer)
                else:
                    # Insert a new customers
                    usertbl_query = "insert into vff.usertbl (usrname,mobile_no,address,age,gender,date_of_birth,pincode,landmark,profile_img) VALUES ('"+str(uname)+"', '"+str(primary_mobno)+"', '"+str(address)+"','"+str(age)+"','"+str(gender)+"','"+str(date_of_birth)+"','"+str(pincode)+"','"+str(land_mark)+"','"+str(image_url)+"') RETURNING usrid"
                    cursor.execute(usertbl_query)
                    usrid = cursor.fetchone()[0]  # Retrieve the returned usrid

                    insert_query = (
                        "insert into vff.laundry_customertbl (usrid,customer_name,query,gstno,company_name,igstno) values "
                        "('"+str(usrid)+"','"+str(uname)+"','"+str(queries)+"','"+str(gstno)+"','"+str(company_name)+"','"+str(igstno)+"')"
                        
                    )
                    print(f"Create New user details::{insert_query}")
                    cursor.execute(insert_query)
                connection.commit()

                print("Customer Added/Updated Successfully.")
                return redirect('dashboard_app:customers')
        except Exception as e:
            print(f"Error loading data: {e}")

    
    
    return render(request,'customer_pages/add_customer.html',{'data':data})


#Add New Staff Page
def add_staff(request,usrid=None):
    
    isLogin = is_loggedin(request)
    if isLogin == False:
        return redirect('dashboard_app:login')
    # If usrid is provided, retrieve the data for the selected Customer
    data = {}
    print(usrid)
    if usrid:
        try:
            with connection.cursor() as cursor:
                cursor.execute("select usrname,mobile_no,usertbl.address,age,gender,emplyid,landmark,date_of_birth,pincode,query,profile_img,branchid,designation,aadharno,dateofjoin from vff.usertbl,vff.laundry_employeetbl where usertbl.usrid=laundry_employeetbl.usrid and laundry_employeetbl.usrid='"+str(usrid)+"'")
                row = cursor.fetchone()
                print(f'fetching the single user data::{row}')
                if row:
                    image_url = row[10]
                    data = {
                        'usrid': usrid,
                        'fullname': row[0],
                        'primaryno': row[1],
                        'fulladdress': row[2],
                        'age': row[3],
                        'gender': row[4],
                        'emplyid': row[5],
                        'landmark': row[6],
                        'dateofbirth': row[7],
                        'pincode': row[8],
                        'questions': row[9],
                        'profile_img': image_url,
                        'branch_id': row[11],
                        'designation': row[12],
                        'aadharno': row[13],
                        'dateofjoin': row[14],
                        
                        
                    }
        except Exception as e:
            print(f"Error loading data: {e}") 
       
    if request.method == "POST":
        uname = request.POST.get('fullname')
        primary_mobno = request.POST.get('primaryno')
        age = request.POST.get('age')
        gender = request.POST.get('gender')
        address = request.POST.get('fulladdress')
        pincode = request.POST.get('pincode')
        land_mark = request.POST.get('landmark')
        date_of_birth = request.POST.get('dateofbirth')
        queries = request.POST.get('questions')
        aadharno = request.POST.get('aadharno')
        designation = request.POST.get('designation')
        dateofjoin = request.POST.get('dateofjoin')
        uploaded_image = request.FILES.get('profile-image1')

        
        if uploaded_image:
            image_url = upload_images2(uploaded_image)
        elif data.get('profile_img'):
            image_url = data.get('profile_img')
        else:
            # Handle the case where there's no uploaded image and no previous image
            image_url = 'NA'  # Set it to a default value or handle accordingly
            
        # image_url = 'NA'
        # if request.FILES.get('profile-image1'):
        #         uploaded_image = request.FILES['profile-image1']
        #         image_url = upload_images2(uploaded_image)
            

        
        
        if not queries:
            queries = 'No queries'
        
        
        errors = []
        if not date_of_birth:
            today_date = timezone.now().date() 
            formatted_date = today_date.strftime('%Y-%m-%d')
            date_of_birth = formatted_date
        if not age:
            age = '-1'
        if not land_mark:
            land_mark = 'NA'
        branch_id = request.session.get('branchid')
        print(f'branch_id:{branch_id}')
        if not branch_id:
            # If there are validation errors, render the form with error messages
            errors = "Please select Branch ID to add new customer"
            return render(request,'customer_pages/add_customer.html',{'data':data,'error':errors})
        
        try:
            with connection.cursor() as cursor:
                if usrid:
                    # Update an existing employee
                    update_query = (
                        "update vff.usertbl set usrname='"+str(uname)+"',mobile_no='"+str(primary_mobno)+"',address='"+str(address)+"',age='"+str(age)+"',gender='"+str(gender)+"',date_of_birth='"+str(date_of_birth)+"',pincode='"+str(pincode)+"',landmark='"+str(land_mark)+"',profile_img='"+str(image_url)+"' where usrid='"+str(usrid)+"'"
                    )
                    print(f"update user details::{update_query}")
                    cursor.execute(update_query)
                    
                    update_customer = (
                        "update vff.laundry_employeetbl set employee_name='"+str(uname)+"', query='"+str(queries)+"', designation='"+str(designation)+"', aadharno='"+str(aadharno)+"',dateofjoin='"+str(dateofjoin)+"' where usrid='"+str(usrid)+"'"
                    )
                    print(f"update employee details::{update_customer}")
                    cursor.execute(update_customer)
                else:
                    # Insert a new employee
                    usertbl_query = "insert into vff.usertbl (usrname,mobile_no,address,age,gender,date_of_birth,pincode,landmark,profile_img) VALUES ('"+str(uname)+"', '"+str(primary_mobno)+"', '"+str(address)+"','"+str(age)+"','"+str(gender)+"','"+str(date_of_birth)+"','"+str(pincode)+"','"+str(land_mark)+"','"+str(image_url)+"') RETURNING usrid"
                    cursor.execute(usertbl_query)
                    usrid = cursor.fetchone()[0]  # Retrieve the returned usrid

                    insert_query = (
                        "insert into vff.laundry_employeetbl (usrid,branchid,employee_name,query,designation,aadharno,dateofjoin) values "
                        "('"+str(usrid)+"','"+str(branch_id)+"','"+str(uname)+"','"+str(queries)+"','"+str(designation)+"','"+str(aadharno)+"','"+str(dateofjoin)+"')"
                        
                    )
                    print(f"Create New user details::{insert_query}")
                    cursor.execute(insert_query)
                connection.commit()

                print("Employee Added/Updated Successfully.")
                return redirect('dashboard_app:all_staff')
        except Exception as e:
            print(f"Error loading data: {e}")

    
    
    return render(request,'staff_pages/add_new_staff_member.html',{'data':data})


#Delete Customers
def delete_customer(request, usrid):
    try:
        with connection.cursor() as cursor:
            # Delete the senior citizen using usrid
            delete_query = "DELETE FROM vff.laundry_customertbl WHERE usrid = '"+str(usrid)+"'"
            cursor.execute(delete_query)
            delete_user_query = "DELETE FROM vff.usertbl WHERE usrid = '"+str(usrid)+"'"
            cursor.execute(delete_user_query)
            connection.commit()

            print(f"Customer  with usrid {usrid} deleted successfully.")
    except Exception as e:
        print(f"Error deleting Customer: {e}")

    return redirect('dashboard_app:customers')

#Delete delivery Boy
def delete_delivery_boy(request, usrid):
    try:
        with connection.cursor() as cursor:
            # Delete the senior citizen using usrid
            delete_query = "DELETE FROM vff.laundry_delivery_boytbl WHERE usrid = '"+str(usrid)+"'"
            cursor.execute(delete_query)
            delete_user_query = "DELETE FROM vff.usertbl WHERE usrid = '"+str(usrid)+"'"
            cursor.execute(delete_user_query)
            connection.commit()

            print(f"Customer  with usrid {usrid} deleted successfully.")
    except Exception as e:
        print(f"Error deleting Customer: {e}")

    return redirect('dashboard_app:customers')

def get_all_delivery_boys(request):
    isLogin = is_loggedin(request)
    if isLogin == False:
        return redirect('dashboard_app:login')
    error_msg = "No Delivery Agents Data Found"
    branch_id = request.session.get('branchid')
    filter = ''
    if branch_id :
        filter = " and laundry_delivery_boytbl.branchid='"+str(branch_id)+"'"
    query = " select laundry_delivery_boytbl.usrid,usrname,mobile_no,usertbl.address,lat,lng,age,gender,laundry_delivery_boytbl.branchid,delivery_boy_id,is_active,is_online,branch_name,usertbl.epoch,profile_img from vff.branchtbl,vff.laundry_delivery_boytbl,vff.usertbl where laundry_delivery_boytbl.usrid=usertbl.usrid and laundry_delivery_boytbl.branchid=branchtbl.branchid  "+filter+" order by usrname desc"
    
    query_result = execute_raw_query(query)
    
    
        
    data = []    
    if not query_result == 500:
        for row in query_result:
            epoch_time = row[13]
            datetime_obj = datetime.utcfromtimestamp(epoch_time)
            gmt_plus_0530 = pytz.timezone('Asia/Kolkata')
            datetime_obj_gmt_plus_0530 = datetime_obj.replace(tzinfo=pytz.utc).astimezone(gmt_plus_0530)
            formatted_datetime = datetime_obj_gmt_plus_0530.strftime('%Y-%m-%d %I:%M:%S %p')
            data.append({
                'usrid': row[0],
                'usrname': row[1],
                'mobno': row[2],
                'address': row[3],
                'lat': row[4],
                'lng': row[5],
                'age': row[6],
                'gender': row[7],
                'branchid': row[8],
                'delivery_boy_id': row[9],
                'active_status': row[10],
                'is_online': row[11],
                'branch_name': row[12],
                'creation_date_time':formatted_datetime,
                'profile_img': row[14],
               
            })
    else:
        error_msg = 'Something Went Wrong'
        
    return JsonResponse({'deliveryBoys':data})
#All Delivery Agents
def all_delivery_agents(request):
    isLogin = is_loggedin(request)
    if isLogin == False:
        return redirect('dashboard_app:login')
    error_msg = "No Delivery Agents Data Found"
    branch_id = request.session.get('branchid')
    filter = ''
    if branch_id :
        filter = " and laundry_delivery_boytbl.branchid='"+str(branch_id)+"'"
    query = " select laundry_delivery_boytbl.usrid,usrname,mobile_no,usertbl.address,lat,lng,age,gender,laundry_delivery_boytbl.branchid,delivery_boy_id,is_active,is_online,branch_name,usertbl.epoch,profile_img from vff.branchtbl,vff.laundry_delivery_boytbl,vff.usertbl where laundry_delivery_boytbl.usrid=usertbl.usrid and laundry_delivery_boytbl.branchid=branchtbl.branchid  "+filter+" order by usrname desc"
    
    query_result = execute_raw_query(query)
    
    
        
    data = []    
    if not query_result == 500:
        for row in query_result:
            epoch_time = row[13]
            datetime_obj = datetime.utcfromtimestamp(epoch_time)
            gmt_plus_0530 = pytz.timezone('Asia/Kolkata')
            datetime_obj_gmt_plus_0530 = datetime_obj.replace(tzinfo=pytz.utc).astimezone(gmt_plus_0530)
            formatted_datetime = datetime_obj_gmt_plus_0530.strftime('%Y-%m-%d %I:%M:%S %p')
            data.append({
                'usrid': row[0],
                'usrname': row[1],
                'mobno': row[2],
                'address': row[3],
                'lat': row[4],
                'lng': row[5],
                'age': row[6],
                'gender': row[7],
                'branchid': row[8],
                'customerid': row[9],
                'active_status': row[10],
                'is_online': row[11],
                'branch_name': row[12],
                'creation_date_time':formatted_datetime,
                'profile_img': row[14],
               
            })
    else:
        error_msg = 'Something Went Wrong'
    current_url = request.get_full_path()
    # using the 'current_url' variable to determine the active card.
    context = {'query_result': data,'current_url': current_url,'error_msg':error_msg}
    
    return render(request, 'delivery_agents_pages/all_delivery_agents.html', context)

#Add Delivery Agent
def add_delivery_agent(request,usrid=None):
    isLogin = is_loggedin(request)
    if isLogin == False:
        return redirect('dashboard_app:login')
     # If usrid is provided, retrieve the data for the selected delievry boy
    data = {}
    print(usrid)
    if usrid:
        try:
            with connection.cursor() as cursor:
                cursor.execute("select usrname,mobile_no,usertbl.address,age,gender,delivery_boy_id,landmark,date_of_birth,pincode,aadhar_no,profile_img,laundry_delivery_boytbl.username,laundry_delivery_boytbl.password"
                               " from vff.laundry_delivery_boytbl,vff.usertbl where laundry_delivery_boytbl.usrid=usertbl.usrid and laundry_delivery_boytbl.usrid='"+str(usrid)+"'")
                row = cursor.fetchone()
                print(f'fetching the single user data::{row}')
                if row:
                    data = {
                        'usrid': usrid,
                        'fullname': row[0],
                        'primaryno': row[1],
                        'fulladdress': row[2],
                        'age': row[3],
                        'gender': row[4],
                        'customerid': row[5],
                        'landmark': row[6],
                        'dateofbirth': row[7],
                        'pincode': row[8],
                        'aadharno': row[9],
                        'profile_img': row[10],
                        'username': row[11],
                        'password': row[12],
                    }
        except Exception as e:
            print(f"Error loading data: {e}") 
      
    if request.method == "POST":
        uname = request.POST.get('fullname')
        primary_mobno = request.POST.get('primaryno')
        age = request.POST.get('age')
        gender = request.POST.get('gender')
        address = request.POST.get('fulladdress')
        pincode = request.POST.get('pincode')
        land_mark = request.POST.get('landmark')
        date_of_birth = request.POST.get('dateofbirth')
        aadharno = request.POST.get('aadharno')
        username = request.POST.get('username')
        password = request.POST.get('password')
        uploaded_image = request.FILES.get('profile-image1')

        
        if uploaded_image:
            image_url = upload_images2(uploaded_image)
        elif data.get('profile_img'):
            image_url = data.get('profile_img')
        else:
            # Handle the case where there's no uploaded image and no previous image
            image_url = 'NA'  # Set it to a default value or handle accordingly
            
        # if request.FILES.get('delivery-image'):
        #     uploaded_image = request.FILES['delivery-image']
        #     image_url = upload_images2(uploaded_image)
        # if request.FILES.get('profile-image1'):
        #     uploaded_image = request.FILES['profile-image1']
        #     image_url = upload_images2(uploaded_image)
        errors = []
        if not date_of_birth:
            today_date = timezone.now().date() 
            formatted_date = today_date.strftime('%Y-%m-%d')
            date_of_birth = formatted_date
        if not age:
            age = '-1'
        if not land_mark:
            land_mark = 'NA'
        
        branch_id = request.session.get('branchid')
        print(f'branch_id:{branch_id}')
        
        
        try:
            with connection.cursor() as cursor:
                if usrid:
                    # Update an existing customers
                    update_query = (
                        "update vff.usertbl set usrname='"+str(uname)+"',mobile_no='"+str(primary_mobno)+"',address='"+str(address)+"',age='"+str(age)+"',gender='"+str(gender)+"',date_of_birth='"+str(date_of_birth)+"',pincode='"+str(pincode)+"',landmark='"+str(land_mark)+"',aadhar_no='"+str(aadharno)+"',profile_img='"+str(image_url)+"' where usrid='"+str(usrid)+"'"
                    )
                    print(f"update user details::{update_query}")
                    cursor.execute(update_query)
                    
                    update_customer = (
                        "update vff.laundry_delivery_boytbl set name='"+str(uname)+"',username='"+str(username)+"',password='"+str(password)+"' where usrid='"+str(usrid)+"'"
                    )
                    print(f"update customer details::{update_customer}")
                    cursor.execute(update_customer)
                else:
                    # Insert a new customers
                    usertbl_query = "insert into vff.usertbl (usrname,mobile_no,address,age,gender,date_of_birth,pincode,landmark,aadhar_no,profile_img) VALUES ('"+str(uname)+"', '"+str(primary_mobno)+"', '"+str(address)+"','"+str(age)+"','"+str(gender)+"','"+str(date_of_birth)+"','"+str(pincode)+"','"+str(land_mark)+"','"+str(aadharno)+"','"+str(image_url)+"') RETURNING usrid"
                    cursor.execute(usertbl_query)
                    usrid = cursor.fetchone()[0]  # Retrieve the returned usrid

                    insert_query = (
                        "insert into vff.laundry_delivery_boytbl (usrid,branchid,name,username,password) values "
                        "('"+str(usrid)+"','"+str(branch_id)+"','"+str(uname)+"','"+str(username)+"','"+str(password)+"')"
                        
                    )
                    print(f"Create New user details::{insert_query}")
                    cursor.execute(insert_query)
                connection.commit()

                print("Delivery Agent Added/Updated Successfully.")
                return redirect('dashboard_app:delivery_agents')
        except Exception as e:
            print(f"Error loading data: {e}")

    
   
    return render (request, 'delivery_agents_pages/add_new_delivery_agent.html',{'data':data})

#Un Assigned Orders
def all_unassigned_orders(request):
    error_msg=""
    query="select orderid,laundry_ordertbl.epoch,pickup_dt,customer_name,order_status,address,mobile_no,profile_img,city,landmark,houseno,device_token from vff.usertbl,vff.laundry_customertbl,vff.laundry_ordertbl where laundry_customertbl.consmrid=laundry_ordertbl.customerid and usertbl.usrid=laundry_customertbl.usrid  and delivery_boyid='-1' and order_status='NA'"
    query_result = execute_raw_query(query)
    data = []    
    if not query_result == 500:
        for row in query_result:
            otepoch = row[1]#order taken epoch
            orderTime = epochToDateTime(otepoch)
            
            data.append({
                'orderid': row[0],
                'orderTime': orderTime,
                'pickup_dt': row[2],
                'customer_name': row[3],
                'order_status': row[4],
                'address': row[5],
                'mobile_no': row[6],
                'profile_img': row[7],
                'city': row[8],
                'landmark': row[9],
                'houseno': row[10],
                'device_token': row[11],
               
                
               
            })
    else:
        error_msg = 'Something Went Wrong'
    current_url = request.get_full_path()
     # using the 'current_url' variable to determine the active card.
    context = {'query_result': data,'current_url': current_url,'error_msg':error_msg}
    return render (request, 'order_pages/all_unassigned_orders.html', context)

#ALL Assigned Bookings
def all_bookings(request):
    error_msg="No Bookings Found"
    branch_id = request.session.get('branchid')
    
    query="select bookingid,customerid,laundry_order_bookingtbl.address,laundry_order_bookingtbl.city,laundry_order_bookingtbl.pincode,laundry_order_bookingtbl.landmark,time_at,booking_status,profile_img,mobile_no,usrname,device_token,name from vff.laundry_delivery_boytbl,vff.usertbl,vff.laundry_customertbl,vff.laundry_order_bookingtbl where laundry_delivery_boytbl.delivery_boy_id=laundry_order_bookingtbl.delivery_boy_id  and laundry_customertbl.consmrid=laundry_order_bookingtbl.customerid and laundry_customertbl.usrid=usertbl.usrid and  laundry_order_bookingtbl.delivery_boy_id!='-1' and booking_status!='NA'  and branch_id='"+str(branch_id)+"' order by bookingid desc"
    query_result = execute_raw_query(query)
    data = []    
    if not query_result == 500:
        for row in query_result:
            otepoch = row[6]#order taken epoch
            orderTime = epochToDateTime(otepoch)
            
            data.append({
                'bookingid': row[0],
                'customerid': row[1],
                'address': row[2],
                'city': row[3],
                'pincode': row[4],
                'landmark': row[5],
                'orderTime': orderTime,
                'order_status': row[7],
                'profile_img': row[8],
                'mobile_no': row[9],
                'customer_name': row[10],
                'device_token': row[11],
                'delivery_boy_name': row[12],
               
                
               
            })
    else:
        error_msg = 'Something Went Wrong'
    current_url = request.get_full_path()
     # using the 'current_url' variable to determine the active card.
    context = {'query_result': data,'current_url': current_url,'error_msg':error_msg}
    return render (request, 'bookings_pages/all_current_bookings.html', context)

#Un Assigned Bookings
def all_unassigned_bookings(request):
    error_msg="No UnAssigned Bookings Found"
    branch_id = request.session.get('branchid')
    query="select bookingid,customerid,laundry_order_bookingtbl.address,laundry_order_bookingtbl.city,laundry_order_bookingtbl.pincode,laundry_order_bookingtbl.landmark,time_at,booking_status,profile_img,mobile_no,usrname,device_token from vff.usertbl,vff.laundry_customertbl,vff.laundry_order_bookingtbl where laundry_customertbl.consmrid=laundry_order_bookingtbl.customerid and laundry_customertbl.usrid=usertbl.usrid and  delivery_boy_id='-1' and booking_status='NA' and branch_id='"+str(branch_id)+"' order by bookingid desc"
    query_result = execute_raw_query(query)
    data = []    
    if not query_result == 500:
        for row in query_result:
            otepoch = row[6]#order taken epoch
            orderTime = epochToDateTime(otepoch)
            
            data.append({
                'bookingid': row[0],
                'customerid': row[1],
                'address': row[2],
                'city': row[3],
                'pincode': row[4],
                'landmark': row[5],
                'orderTime': orderTime,
                'order_status': row[7],
                'profile_img': row[8],
                'mobile_no': row[9],
                'customer_name': row[10],
                'device_token': row[11],
               
                
               
            })
    else:
        error_msg = 'Something Went Wrong'
    current_url = request.get_full_path()
     # using the 'current_url' variable to determine the active card.
    context = {'query_result': data,'current_url': current_url,'error_msg':error_msg}
    return render (request, 'bookings_pages/all_unassigned_bookings.html', context)



#All Orders
def all_orders(request):
    isLogin = is_loggedin(request)
    if isLogin == False:
        return redirect('dashboard_app:login')
    error_msg = "No Orders Data Found"
    branch_id = request.session.get('branchid')
    query = "select consmrid,usertbl.usrid,customer_name,mobile_no,houseno,address,city,pincode,landmark,profile_img,device_token,orderid,delivery_boyid,quantity,price,pickup_dt,delivery,clat,clng,order_completed,order_status,additional_instruction,laundry_ordertbl.epoch,cancel_reason,feedback,delivery_epoch,name as deliveryboy_name from vff.laundry_ordertbl,vff.laundry_customertbl,vff.usertbl,vff.laundry_delivery_boytbl where laundry_customertbl.usrid=usertbl.usrid and laundry_ordertbl.customerid=laundry_customertbl.consmrid and laundry_ordertbl.delivery_boyid=laundry_delivery_boytbl.delivery_boy_id and order_status !='NA' and branch_id='"+str(branch_id)+"'  order by orderid desc"
    query_result = execute_raw_query(query)
    
    
        
    data = []    
    if not query_result == 500:
        for row in query_result:
            depoch = row[25]#delivery epoch
            oepoch = row[22]#order taken epoch
            orderStatus = row[20]
            deliveryEpoch = epochToDateTime(depoch)
            orderTakenEpoch = epochToDateTime(oepoch)
            if orderStatus != "Completed":
                deliveryEpoch = "Not Delivered Yet"
            
            data.append({
                'consmrid': row[0],
                'usrid': row[1],
                'customer_name': row[2],
                'mobile_no': row[3],
                'houseno': row[4],
                'address': row[5],
                'city': row[6],
                'pincode': row[7],
                'landmark': row[8],
                'profile_img': row[9],
                'device_token': row[10],
                'orderid': row[11],
                'delivery_boyid': row[12],
                'quantity':row[13],
                'price': row[14],
                'pickup_dt': row[15],
                'delivery_dt': row[16],
                'clat': row[17],
                'clng': row[18],
                'order_completed': row[19],
                'order_status': orderStatus,
                'additional_instruction': row[21],
                'order_taken_epoch': orderTakenEpoch,
                'cancel_reason': row[23],
                'feedback': row[24],
                'delivery_epoch': deliveryEpoch,
                'delivery_boy_name': row[26],
                
                
               
            })
    else:
        error_msg = 'Something Went Wrong'
    current_url = request.get_full_path()
     # using the 'current_url' variable to determine the active card.
    context = {'query_result': data,'current_url': current_url,'error_msg':error_msg}
    return render (request, 'order_pages/all_orders.html', context)

#Create New Order
def create_new_order(request):
    isLogin = is_loggedin(request)
    if isLogin == False:
        return redirect('dashboard_app:login')
    return render (request, 'order_pages/create_new_order.html')

#View Order Details
def view_order_detail(request,orderid):
    request.session['order_id'] = ""
    isLogin = is_loggedin(request)
    if isLogin == False:
        return redirect('dashboard_app:login')
    error_msg = "No Order Details Found"
    alert_delivery_boy = request.GET.get('no_delivery', None)
    #query_token = "select usertbl.usrid,mobile_no,profile_img,device_token,delivery_boy_id,usrname from vff.laundry_delivery_boytbl,vff.usertbl where usertbl.usrid=laundry_delivery_boytbl.usrid and is_online='1' and status='Free'"
    # alert_delivery_boy =""
    # result = execute_raw_query_fetch_one(query_token)
    # if result:  
    #     device_token = result[2]
    #     delivery_boy_id = result[3]
    #     usrname = result[0] 
    # else:
    #     alert_delivery_boy = "No Delivery Boy is Free To Recieve Orders"
    query = "select consmrid,usertbl.usrid,customer_name,mobile_no,houseno,address,city,pincode,landmark,profile_img,device_token,orderid,delivery_boyid,quantity,price,pickup_dt,delivery,clat,clng,order_completed,order_status,additional_instruction,laundry_ordertbl.epoch,cancel_reason,feedback,delivery_epoch,name as deliveryboy_name,categoryid,subcategoryid,booking_type,dt,cat_img,cat_name,sub_cat_name,sub_cat_img,actual_cost,time,item_cost,item_quantity,type,section_type,laundry_ordertbl.booking_id,gstamount,igstamount,discount_price,order_taken_on,delivery_price,wants_delivery from vff.laundry_active_orders_tbl,vff.laundry_ordertbl,vff.laundry_customertbl,vff.usertbl,vff.laundry_delivery_boytbl where laundry_customertbl.usrid=usertbl.usrid and laundry_ordertbl.customerid=laundry_customertbl.consmrid and laundry_ordertbl.delivery_boyid=laundry_delivery_boytbl.delivery_boy_id and laundry_active_orders_tbl.order_id=laundry_ordertbl.orderid and orderid='"+str(orderid)+"' order by orderid desc;"
    
    query_result = execute_raw_query(query)
    print(f'query_result:::{query_result}')
    
        
    data = []
    sub_items = []    
    if not query_result == 500:
        for row in query_result:
            depoch = row[25]#delivery epoch
            oepoch = row[22]#order taken epoch
            orderStatus = row[20]
            item_cost_str = row[37]
            item_cost = float(item_cost_str)
            formatted_cost = '{:.2f}'.format(item_cost)
            print("Delivery Epoch:"+str(depoch))
            print("Order Taken Epoch:"+str(oepoch))
            deliveryEpoch = epochToDateTime(depoch)
            orderTakenEpoch = epochToDateTime(oepoch)
            if orderStatus != "Completed":
                deliveryEpoch = "Not Delivered Yet"
            cat_name=row[32]
            if cat_name != 'DRY CLEAN':
                sub_items.append(row[33])
            
            data.append({
                'consmrid': row[0],
                'usrid': row[1],
                'customer_name': row[2],
                'mobile_no': row[3],
                'houseno': row[4],
                'address': row[5],
                'city': row[6],
                'pincode': row[7],
                'landmark': row[8],
                'profile_img': row[9],
                'device_token': row[10],
                'orderid': row[11],
                'delivery_boyid': row[12],
                'quantity':row[13],
                'price': row[14],
                'pickup_dt': row[15],
                'delivery_dt': row[16],
                'clat': row[17],
                'clng': row[18],
                'order_completed': row[19],
                'order_status': orderStatus,
                'additional_instruction': row[21],
                'order_taken_epoch': orderTakenEpoch,
                'cancel_reason': row[23],
                'feedback': row[24],
                'delivery_epoch': deliveryEpoch,
                'delivery_boy_name': row[26],
                'categoryid': row[27],
                'subcategoryid': row[28],
                'ordertype': row[29],
                'dt': row[30],
                'cat_img': row[31],
                'cat_name': row[32],
                'sub_cat_name': row[33],
                'sub_cat_img': row[34],
                'actual_cost': row[35],
                'time': row[36],
                'item_cost': formatted_cost,
                'item_quantity': row[38],
                'type_of': row[39],
                'section_type': row[40],
                'booking_id': row[41],
                'gstamount': row[42],
                'igstamount': row[43],
                'discount_price': row[44],
                'order_taken_on': row[45],
                'delivery_price_taken': row[46],
                'wants_delivery': row[47],
                
                
               
            })
        
        #Payment Details
        payment_id = 'Payment Not Done'
        query_payment = "select razor_pay_payment_id,status,time,dt,payment_type from vff.laundry_payment_tbl where order_id='"+str(orderid)+"'"
        pay_result = execute_raw_query_fetch_one(query_payment)
        if pay_result:   
            payment_id = pay_result[0]
            payment_type = pay_result[4]
        
        
        #extra_cart_item like softner
        extra_error = "No Extra Items added"
        extra_query = "select extra_item_name,price from vff.laundry_cart_extra_items_tbl where order_id='"+str(orderid)+"'"
        extra_query_result = execute_raw_query(extra_query)
        extra_data = []    
        if not extra_query_result == 500:
            for row in extra_query_result:
                extra_data.append({
                    'extra_item_name':row[0],
                    'extra_item_price':row[1]
                })
        #delivery charges
        delivery_price = 0
        total_laundry_cost = 0
        range_price = 0
        delivery_query = "select price,range  from vff.laundry_delivery_chargetbl"
        dlvrych_result = execute_raw_query_fetch_one(delivery_query)
        if dlvrych_result:   
            delivery_price = dlvrych_result[0]
            range_price = dlvrych_result[1]
        
        extra_item_sum = sum(extra['extra_item_price'] for extra in extra_data)

        total_laundry_cost = sum(round(float(item['item_cost']), 2) for item in data)
        print(f'total_laundry_cost::{total_laundry_cost}')
        print(f'extra_item_sum::{extra_item_sum}')
        print(f'delivery_price::{delivery_price}')
        
        # if total_laundry_cost != 0:
        #     if total_laundry_cost < range_price:
        #         total_laundry_cost += delivery_price
        #         print(f'Updating TotalCost:{total_laundry_cost}')
        #     else:
        #         delivery_price = 0
        
        #request.session['branchid'] = branchid
        branch_name = request.session.get('branch_name') 
        branch_address = request.session.get('branch_address') 
        branch_gstno = request.session.get('branch_gstno')
        branch_igstno = request.session.get('branch_igstno')
        branch_city = request.session.get('branch_city')
        branch_state = request.session.get('branch_state')
        branch_pincode = request.session.get('branch_pincode')
        branch_contactno = request.session.get('branch_contactno')
        
        
        total_cost = total_laundry_cost + extra_item_sum
        print(f'total_cost::{total_cost}')
        
        sub_total = total_laundry_cost
        
        #Calculating GST For state and central govt
        gstamount = data[0]['gstamount'] if data else ''
        igstamount = data[0]['igstamount'] if data else ''
        print(f'igstamount:::{igstamount}')
        print(f'gstamount:::{gstamount}')
        state_gst = 0
        central_gst = 0
        gst_amount = '0'
        if gstamount != 0 and gstamount != 0.0 :
            totalGST = (total_cost * 18) / 100
            print(f'totalGST::{totalGST}')
            state_gst = gstamount / 2
            central_gst = gstamount / 2
            gst_amount = gstamount
            if total_cost < range_price:
                total_cost += gstamount + delivery_price
            else:
                total_cost += gstamount
                delivery_price = 0
        else:
            if total_cost < range_price:
                total_cost += igstamount + delivery_price
            else:
                total_cost += igstamount 
                delivery_price =0
        
        igstamount = round(igstamount,2)
        if igstamount == 0.0:
            igstamount = '0.0'
        
        first_order_id = data[0]['orderid'] if data else ''
        discount_amount = data[0]['discount_price'] if data else ''
        booking_id = data[0]['booking_id'] if data else ''
        mobile_no = data[0]['mobile_no'] if data else ''
        customer_name = data[0]['customer_name'] if data else ''
        address = data[0]['address'] if data else ''
        houseno = data[0]['houseno'] if data else ''
        city = data[0]['city'] if data else ''
        pincode = data[0]['pincode'] if data else ''
        landmark = data[0]['landmark'] if data else ''
        order_status = data[0]['order_status'] if data else ''
        order_taken_on = data[0]['order_taken_on'] if data else ''
        delivery_price_taken = data[0]['delivery_price_taken'] if data else ''
        order_completed = data[0]['order_completed'] if data else ''
        order_date = data[0]['order_taken_epoch'] if data else ''
        delivery_date = data[0]['delivery_epoch'] if data else ''
        additional_instruction = data[0]['additional_instruction'] if data else ''
        wants_delivery = data[0]['wants_delivery'] if data else ''
        request.session['order_id'] = first_order_id
        order_completed_status = ""
        if order_completed == 0:
            order_completed_status = "Accepted"
        elif order_completed == 1:
            order_completed_status = "Completed"
        elif order_completed_status == 2:
            order_completed_status = "Cancelled"
            
        print(f'OrderID::{first_order_id}')
        print(f'sub_items:::{sub_items}')
        
        print(f'wants_delivery:::{wants_delivery}')
        print(f'order_taken_on:::{order_taken_on}')
        
    else:
        error_msg = 'Something Went Wrong'
    
    context ={'query_result':data,'extra_data':extra_data,'error_msg':error_msg,'payment_id':payment_id,'order_id':first_order_id,'customer_name':customer_name
              ,'address':address,'houseno':houseno,'city':city,'pincode':pincode,'landmark':landmark,'order_status':order_status,'order_completed_status':order_completed_status,'order_date':order_date,'delivery_date':delivery_date,'extra_item_sum':extra_item_sum,'delivery_price':delivery_price,'total_cost':round(total_cost,2),'extra_error':extra_error,'range_price':range_price,'alert_delivery_boy':alert_delivery_boy,'sub_items':sub_items,'booking_id':booking_id,'mobile_no':mobile_no,'branch_address':branch_address,'branch_name':branch_name,'branch_gstno':branch_gstno,'branch_igstno':branch_igstno,'branch_city':branch_city,'branch_state':branch_state,'branch_pincode':branch_pincode,'branch_contactno':branch_contactno,'payment_type':payment_type,'gst_amount':gst_amount,'discount_amount':round(discount_amount,2),'sub_total':round(sub_total,2),'additional_instruction':additional_instruction,'order_taken_on':order_taken_on,'delivery_price_taken':delivery_price_taken,'wants_delivery':wants_delivery,'state_gst':round(state_gst,2),'central_gst':round(central_gst,2),'igstamount':igstamount}
    
    return render(request,'order_pages/order_details.html',context)

#To Send notification to delivery boy for order ID
def send_notification_to_delivery_boy(order_id,title,body,data,order_status,delivery_boy_id_default):
    showAlert = ""
    usrname = ""
    delivery_boy_id = "-1"
    print(f'checking while notify delivery_boy_id_default::{delivery_boy_id_default}')
    if delivery_boy_id_default =='-1':
        
        query_token = "select usrname,mobile_no,device_token,delivery_boy_id from vff.usertbl,vff.laundry_delivery_boytbl,vff.laundry_ordertbl where usertbl.usrid=laundry_delivery_boytbl.usrid and laundry_ordertbl.delivery_boyid=laundry_delivery_boytbl.delivery_boy_id and orderid='"+str(order_id)+"'"
    else:
        query_token="select usrname,mobile_no,device_token,delivery_boy_id,profile_img,usertbl.usrid from vff.laundry_delivery_boytbl,vff.usertbl where usertbl.usrid=laundry_delivery_boytbl.usrid and delivery_boy_id='"+str(delivery_boy_id_default)+"'"
    # if order_status == "Out for Delivery" or order_status=="Assigning":
    #     query_token = "select usrname,mobile_no,device_token,delivery_boy_id,profile_img,usertbl.usrid from vff.laundry_delivery_boytbl,vff.usertbl where usertbl.usrid=laundry_delivery_boytbl.usrid and is_online='1' and status='Free'"
    # else:
    #     query_token = "select usrname,mobile_no,device_token,delivery_boy_id from vff.usertbl,vff.laundry_delivery_boytbl,vff.laundry_ordertbl where usertbl.usrid=laundry_delivery_boytbl.usrid and laundry_ordertbl.delivery_boyid=laundry_delivery_boytbl.delivery_boy_id and orderid='"+str(order_id)+"'"
    
    result = execute_raw_query_fetch_one(query_token)
    if result:  
        device_token = result[2]
        delivery_boy_id = result[3]
        usrname = result[0] 
        
        
        title = title
        msg = body
        data = data 
        
        sendFMCMsg(device_token,msg,title,data)
        showAlert = ""
        print(f'Notification sent to {usrname} successfully')
    else:
        showAlert = "No Delivery Boy is Free to Take Orders"
        print('No Delivery Boy is Free to Take Order')
    return showAlert,delivery_boy_id,usrname
        
#To Send notification to customer for order ID
def send_notification_customer(order_id,title,body,data=None):
    showAlert = ""
    query_customer = "select usrname,device_token,customerid from vff.laundry_customertbl,vff.usertbl,vff.laundry_ordertbl where usertbl.usrid=laundry_customertbl.usrid and laundry_ordertbl.customerid=laundry_customertbl.consmrid and orderid='"+str(order_id)+"'"
    cresult = execute_raw_query_fetch_one(query_customer)
    print(f'Customer_query::{cresult}')
    if cresult:   
        
        usrname = cresult[0]
        cdevice_token = cresult[1]
        customerid = cresult[2]
        print(f'CustomersToken::{cdevice_token}')
        
        
        title = title
        msg = body
        data = data
        sendFMCMsg(cdevice_token,msg,title,data)
        showAlert = f"Notification sent to {usrname} Customer successfully"
        print(f'Notification sent to {usrname} successfully')
    else:
        showAlert = "Notification was not sent to Customer"
    return showAlert,customerid

#Accept Delivery or Assigned Delivery to
def delivery_accept(request,booking_id,delivery_boy_id):
    if request.method == "POST": 
        branch_id = request.session.get('branchid')
        #Checking if the Order/ Booking id is assigned or not
        query_check = "select delivery_boy_id,bookingid,branch_id from vff.laundry_order_bookingtbl where bookingid='"+str(booking_id)+"'"
        cresult = execute_raw_query_fetch_one(query_check)
        print(f'delivery_accept_query_check::{cresult}')
        if cresult:
            delivery_boyid = cresult[0] #Selected from DB
            bookingid = cresult[1]
            print(f'DB delivery_boyid::{delivery_boyid}')
            if delivery_boyid != -1:
                query_order_check = "select orderid from vff.laundry_ordertbl where booking_id='"+str(booking_id)+"'"
                oresult = execute_raw_query_fetch_one(query_order_check)
                print(f'Order Status Check::{oresult}')   
                if oresult:
                    order_id = oresult[0]
                    return redirect('dashboard_app:all_orders')
                #TODO:Send to Current Bookings Page
                return redirect('dashboard_app:all_bookings')
            else:
                    try:
                        with connection.cursor() as cursor:
                            print('Assigning Delivery Boy')
                            title="VFF Group Order Assigned"
                            body = "New Order assigned by admin for Booking ID #"+str(booking_id)+""
                            data={
                                'booking_id':str(booking_id)
                            }
                            intent = "MainRoute"
                            order_status = "Accepted"
                            #query_token = "select usrname,mobile_no,device_token,delivery_boy_id,profile_img,usertbl.usrid from vff.laundry_delivery_boytbl,vff.usertbl where usertbl.usrid=laundry_delivery_boytbl.usrid and is_online='1' and status='Free' and delivery_boy_id='"+str(delivery_boy_id)+"'"
                            query_token = "select usrname,mobile_no,device_token,delivery_boy_id,profile_img,usertbl.usrid from vff.laundry_delivery_boytbl,vff.usertbl where usertbl.usrid=laundry_delivery_boytbl.usrid and is_online='1' and delivery_boy_id='"+str(delivery_boy_id)+"'"
                            result = execute_raw_query_fetch_one(query_token)
                            if result:  
                                device_token = result[2] 
                                sendFMCMsg(device_token,body,title,data)
                            status = "Accepted"
                            query = "insert into vff.laundry_delivery_accept_tbl(delivery_boy_id,status,booking_id,branch_id) values ('"+str(delivery_boy_id)+"','"+str(status)+"','"+str(booking_id)+"','"+str(branch_id)+"')"
                            print(f'Updating To Busy Status::{query}')
                            cursor.execute(query)
                            connection.commit()
                            query2="update vff.laundry_order_bookingtbl set delivery_boy_id='"+str(delivery_boy_id)+"',booking_status='"+str(status)+"' where bookingid='"+str(booking_id)+"'"
                            cursor.execute(query2)
                            connection.commit()
                            query3="update vff.laundry_delivery_boytbl set status='Busy' where delivery_boy_id='"+str(delivery_boy_id)+"'"
                            cursor.execute(query3)
                            connection.commit()
                            #Order Assignment Table
                            query4="insert into vff.laundry_order_assignmenttbl(booking_id,delivery_boy_id,type_of_order) values ('"+str(booking_id)+"','"+str(delivery_boy_id)+"','Pickup')"
                            cursor.execute(query4)
                            connection.commit()

                            return redirect('dashboard_app:all_bookings')
                    except Exception as e:
                        print(e)
    return redirect('dashboard_app:all_unassigned_orders')
#Assign Delivery Boy to Order ID
def assigned_delivery_boy(request,orderid):
    branch_id = request.session.get('branchid')
    error_msg = "No Delivery Agents Created"
    query = "select delivery_boy_id,name,is_online,status,profile_img,mobile_no,address from vff.usertbl,vff.laundry_delivery_boytbl where laundry_delivery_boytbl.usrid=usertbl.usrid and branchid='"+str(branch_id)+"'"
    query_result = execute_raw_query(query)
       
    data = []    
    if not query_result == 500:
        for row in query_result:
             data.append({
                 'delivery_boy_id':row[0],
                 'name':row[1],
                 'is_online':row[2],
                 'status':row[3],
                 'profile_img':row[4],
                 'mobile_no':row[5],
                 'address':row[6],
                 
             })
    else:
        error_msg = 'Something Went Wrong'
    current_url = request.get_full_path()
     # using the 'current_url' variable to determine the active card.
    context = {'query_result': data,'current_url': current_url,'error_msg':error_msg,'order_id':orderid}
    return render(request,'order_pages/all_assigning_delivery_boy.html',context)

# def update_order_status(request,order_id,booking_id):
#     alert_delivery_boy = ""
#     if request.method == "POST":
#         order_status = request.POST.get('order-status')
#         order_taken_on = request.POST.get('order_taken_on')
#         delivery_price = request.POST.get('delivery_price')
#         wants_delivery = request.POST.get('wants_delivery')
#         delivery_boy_id_default = '-1'
#         if 'delivery-boy' in request.POST:
#             delivery_boy_id_default = request.POST.get('delivery-boy')
#         # order_id = request.session.get('order_id')
#         userid = request.session.get('userid')
#         order_completed  = "0"
#         if order_status == "Completed":
#             order_completed = "1"
#         elif order_status == "Cancelled":
#             order_completed = "2"
#         else:
#             order_completed = "0"
#         print(f'Currentorder_status::{order_status}')
#         print(f'Current_order_taken_on::{order_taken_on}')
#         print(f'Current_delivery_price::{delivery_price}')
        
#         #To Check if Order is Already Assigned to Someone or what
#         if (order_status == "Out for Delivery" and order_taken_on == 'App') or (wants_delivery == '1' and order_taken_on == 'OnCounter' and order_status == "Out for Delivery"):
#             print('Entering Here Now')
#             query_check = "select delivery_boy_id,orderid from vff.laundry_order_assignmenttbl,vff.laundry_ordertbl where laundry_ordertbl.orderid=laundry_order_assignmenttbl.order_id and laundry_ordertbl.booking_id=laundry_order_assignmenttbl.booking_id and type_of_order='Drop' and laundry_order_assignmenttbl.order_id='"+str(order_id)+"'"
#             cresult = execute_raw_query_fetch_one(query_check)
#             if cresult:
#                 alert_delivery_boy = "Delivery boy Already Assigned To this Order."
#                 redirect_url = reverse('dashboard_app:view_order_detail', kwargs={'orderid': order_id})
#                 redirect_url += f'?no_delivery={alert_delivery_boy}'
#                 return HttpResponseRedirect(redirect_url)
#             #Sending Notification to Delivery Boy who is free to take orders
#             query_token = "select usrname,mobile_no,device_token,delivery_boy_id from vff.usertbl,vff.laundry_delivery_boytbl,vff.laundry_ordertbl where usertbl.usrid=laundry_delivery_boytbl.usrid and laundry_ordertbl.delivery_boyid=laundry_delivery_boytbl.delivery_boy_id and orderid='"+str(order_id)+"'"
#             result = execute_raw_query_fetch_one(query_token)
#             if result:  
#                 usrname = result[0] 
#                 delivery_boy_id = result[3]
#                 device_token = result[2]
#                 try:
#                     with connection.cursor() as cursor:
#                         update_free = "update vff.laundry_delivery_boytbl set status='Free' where delivery_boy_id='"+str(delivery_boy_id)+"'"
#                         cursor.execute(update_free)
#                         connection.commit()

#                 except Exception as e:
#                     print(f"Error loading data: {e}")
#         condition = wants_delivery == '1' and order_taken_on == "OnCounter" and order_status == "Completed"
#         print(f'Condition::{condition}')            
#         #if ((order_status == "Out for Delivery" and order_taken_on == 'App') or (delivery_price != '0.0' and order_taken_on == 'OnCounter' and order_status == "Out for Delivery")) or ((order_status == "Completed" and order_taken_on == 'App') or condition) or order_status == "Processing" or order_status == "Pick Up Done" or order_status== "Reached Store":
#         if ((order_status == "Out for Delivery" and order_taken_on == 'App') or (wants_delivery == '1' and order_taken_on == 'OnCounter' and order_status == "Out for Delivery")):   
#             print('Entering Here Now to send notification to delivery boy')
#             #To Send for Delivery Boy
#             if order_status !="Processing":
#                 title = "VFF Group"
#                 msg = "Delivery Package is ready pick it up from store"
#                 if order_status == "Completed":
#                     title = "Order Completed"
#                     msg = "Laundry Package Delivery Successfully. Now You are free to accept new Orders"
#                 # elif order_status == "Processing":
#                 #     msg = "Processing has been started for Order ID : #"+str(order_id)+". You are now free to recieve new orders."
#                 elif order_status == "Pick Up Done":
#                     title = "Pick Up Done"
#                     msg = "Laundry PickUp Done for Order ID : #"+str(order_id)+""
#                 elif order_status == "Reached Store":
#                     title = "Reached Store"
#                     msg = "Now you are ready to Receive New Orders."
#                 else:
#                     msg = "Order ID #"+str(order_id)+" Assigned.\nDelivery Package is ready pick it up from store"

#                 data = {

#                      'order_id_pickup':order_id
#                      }
#                 notifyDeliveryBoy,deliveryBoyID,deliveryBOYName = send_notification_to_delivery_boy(order_id,title,msg,data,order_status)
#                 print(f'deliveryBoyID::{deliveryBoyID}')
#                 print(f"notifyDeliveryBoy::{notifyDeliveryBoy}")
                
            
#                 if (order_status == "Out for Delivery" and deliveryBoyID != '-1' ):
#                     try:
#                         with connection.cursor() as cursor:
#                             filter = ""

#                             if order_status == "Out for Delivery" and deliveryBoyID != '-1':
#                                 filter = ",delivery_boyid='"+str(deliveryBoyID)+"'"
#                             query = "update vff.laundry_ordertbl set order_status='"+str(order_status)+"',order_completed='"+str(order_completed)+"'"+filter+" where orderid='"+str(order_id)+"'"
#                             print(f'Updating To Busy Status::{query}')
#                             cursor.execute(query)
#                             connection.commit()
                            
#                             #Insert While Assigning Order for delivery
#                             query_assign = "insert into vff.laundry_order_assignmenttbl (booking_id,order_id,delivery_boy_id,type_of_order) values ('"+str(booking_id)+"','"+str(order_id)+"','"+str(deliveryBoyID)+"','Drop')"
#                             print(f'Inserting Assing to Drop::{query_assign}')
#                             cursor.execute(query_assign)
#                             connection.commit()
                            
#                             #Make Him In Busy Mode
#                             query3="update vff.laundry_delivery_boytbl set status='Busy' where delivery_boy_id='"+str(deliveryBoyID)+"'"
#                             cursor.execute(query3)
#                             print(f'Putting Delivery Boy to busy mode::{query3}')
#                             connection.commit()
#                     except Exception as e:
#                         print(e)
#                 else:
#                     print('No Delivery Boy is Available to Take Orders')
#                     alert_delivery_boy = "No Delivery Boy is Free To Receive Orders"
#                     redirect_url = reverse('dashboard_app:view_order_detail', kwargs={'orderid': order_id})
#                     redirect_url += f'?no_delivery={alert_delivery_boy}'
#                     return HttpResponseRedirect(redirect_url)
#                     #redirect(reverse('dashboard_app:view_order_detail', kwargs={'orderid': order_id}))
            
#             if order_status == "Out for Delivery" and deliveryBoyID != '-1':
                
#                 jfilter = "" 
#                 status = ""
#                 if order_status == "Out for Delivery":
#                     jfilter =",delivery_boyid"
#                     status = "Busy"
#                 else:
#                     jfilter = ",delivery_boy_id"
#                     status = "Free"
#                 query_token = "select usrname,mobile_no,device_token"+jfilter+" from vff.usertbl,vff.laundry_delivery_boytbl,vff.laundry_ordertbl where usertbl.usrid=laundry_delivery_boytbl.usrid and laundry_ordertbl.delivery_boyid=vff.laundry_delivery_boytbl.delivery_boy_id and orderid='"+str(order_id)+"'"
#                 result = execute_raw_query_fetch_one(query_token)
#                 if result:  
#                     usrname = result[0] 
#                     delivery_boy_id = result[3]
#                     device_token = result[2]
                    
#                     try:
#                         with connection.cursor() as cursor:
#                             update_free = "update vff.laundry_delivery_boytbl set status='"+str(status)+"' where delivery_boy_id='"+str(delivery_boy_id)+"'"
#                             cursor.execute(update_free)
#                             connection.commit()

#                     except Exception as e:
#                         print(f"Error loading data: {e}")
                
            
#         #To send to customer
#         title = "VFF Group"
#         if order_status == "Completed":
#             title = "Order Completed"
#             msg = "Laundry Package Delivery Successfully for Order ID : #"+str(order_id)+" . Keep Ordering with Velvet Wash"
#         elif order_status == "Processing":
#             title = "Processing Status"
#             msg = "Processing has been started for your Order ID : #"+str(order_id)+""
#         elif order_status == "Pick Up Done":
#             title = "Pick Up Done"
#             msg = "Laundry PickUp Done for Order ID : #"+str(order_id)+""
#         elif order_status == "Reached Store":
#             title = "Reached Store"
#             msg = "Your Laundry has arrived at Store for Order ID : #"+str(order_id)+".\nWe will ping you once the processing has been started Thank you."
#         elif order_status == "Ready for Delivery":
#             title = "Ready For Delivery"
#             msg = "Your Laundry Package is Ready For Delivery for Order ID : #"+str(order_id)+".\nThank you."
#         else:
#             msg = "Your Laundry Package is on its way to deliver for Order ID : #"+str(order_id)+""
#         data = {
#              'intent':'MainRoute',
#              }
#         notifyCustomer,customerid = send_notification_customer(order_id,title,msg,data)
        
        
#         try:
#             with connection.cursor() as cursor:
#                 filter = ""
#                 if order_status == "Completed":
#                     current_timestamp = time.time()
#                     current_datetime = datetime.now().strftime("%Y-%m-%d")
#                     filter = ",delivery='"+str(current_datetime)+"',delivery_epoch='"+str(current_timestamp)+"'"
#                 if order_status == "Out for Delivery" and deliveryBoyID != '-1':
#                     filter = ",delivery_boyid='"+str(delivery_boy_id)+"'"
#                 query = "update vff.laundry_ordertbl set order_status='"+str(order_status)+"',order_completed='"+str(order_completed)+"'"+filter+" where orderid='"+str(order_id)+"'"
#                 print(f'----------------------------------- Updating Order ID with delivery Epoch ----------------')
#                 print(f'query_update::{query}')
#                 cursor.execute(query)
#                 connection.commit()
#                 query2 = "insert into vff.laundry_order_historytbl(order_id,order_stages) values ('"+str(order_id)+"','"+str(order_status)+"')"
#                 cursor.execute(query2)
#                 connection.commit()
#                 #Insert Delivery Boy Record
#                 if order_status != "Processing" and order_status !="Ready for Delivery":
#                     insert_notify="insert into vff.laundry_notificationtbl(title,body,reciever_id,sender_id,order_id) values ('"+str(title)+"','"+str(msg)+"','"+str(delivery_boy_id)+"','"+str(userid)+"','"+str(order_id)+"')"
#                     cursor.execute(insert_notify)
#                     print(f'Notification inserted for Delivery Boy::{insert_notify}')
#                     connection.commit()
#                 #Insert Customers Record
#                 cinsert_notify="insert into vff.laundry_notificationtbl(title,body,reciever_id,sender_id,order_id) values ('"+str(title)+"','"+str(msg)+"','"+str(customerid)+"','"+str(userid)+"','"+str(order_id)+"')"
#                 cursor.execute(cinsert_notify)
#                 connection.commit()
#                 print(f'Notification inserted for Customers::{cinsert_notify}')
#                 print("Order Status Updated Successfully")
#                 return redirect(reverse('dashboard_app:view_order_detail', kwargs={'orderid': order_id}))
#         except Exception as e:
#                 print(f"Error loading data: {e}")
            
                
#         else:
#             #Only when Delivery boy is not needed to update status
            
#             try:
#                 with connection.cursor() as cursor:
#                     query2 = "insert into vff.laundry_order_historytbl(order_id,order_stages) values ('"+str(order_id)+"','"+str(order_status)+"')"
#                     cursor.execute(query2)
#                     connection.commit()
#                     query = "update vff.laundry_ordertbl set order_status='"+str(order_status)+"',order_completed='"+str(order_completed)+"' where orderid='"+str(order_id)+"'"    
#                     print(f'query_update::{query}')
#                     cursor.execute(query)
#                     connection.commit()
#                     #Insert Customers Record
#                     cinsert_notify="insert into vff.laundry_notificationtbl(title,body,reciever_id,sender_id,order_id) values ('"+str(title)+"','"+str(msg)+"','"+str(customerid)+"','"+str(userid)+"','"+str(order_id)+"')"
#                     cursor.execute(cinsert_notify)
#                     connection.commit()
#                     print("Order Status Updated Successfully")
#             except Exception as e:
#                     print(f"Error loading data: {e}")
                   
#     return redirect(reverse('dashboard_app:view_order_detail', kwargs={'orderid': order_id}))

#Upadting New Order Status [OLD Code is Above only]     
def update_order_status_new(request,order_id,booking_id):
    alert_delivery_boy = ""
    if request.method == "POST":
        order_status = request.POST.get('order-status')
        order_taken_on = request.POST.get('order_taken_on')
        delivery_price = request.POST.get('delivery_price')
        wants_delivery = request.POST.get('wants_delivery')
        delivery_boy_id_default = '-1'
        if 'delivery-boy' in request.POST:
            delivery_boy_id_default = request.POST.get('delivery-boy')
            if not delivery_boy_id_default:
                delivery_boy_id_default='-1'
        # order_id = request.session.get('order_id')
        userid = request.session.get('userid')
        order_completed  = "0"
        if order_status == "Completed":
            order_completed = "1"
        elif order_status == "Cancelled":
            order_completed = "2"
        else:
            order_completed = "0"
        print(f'Currentorder_status::{order_status}')
        print(f'Current_order_taken_on::{order_taken_on}')
        print(f'Current_delivery_price::{delivery_price}')
        
        #To Check if Order is Already Assigned to Someone or what
        if (order_status == "Out for Delivery" and order_taken_on == 'App') or (wants_delivery == '1' and order_taken_on == 'OnCounter' and order_status == "Out for Delivery"):
            print('Entering Here Now')
            query_check = "select delivery_boy_id,orderid from vff.laundry_order_assignmenttbl,vff.laundry_ordertbl where laundry_ordertbl.orderid=laundry_order_assignmenttbl.order_id and laundry_ordertbl.booking_id=laundry_order_assignmenttbl.booking_id and type_of_order='Drop' and laundry_order_assignmenttbl.order_id='"+str(order_id)+"'"
            cresult = execute_raw_query_fetch_one(query_check)
            if cresult:
                alert_delivery_boy = "Delivery boy Already Assigned To this Order."
                redirect_url = reverse('dashboard_app:view_order_detail', kwargs={'orderid': order_id})
                redirect_url += f'?no_delivery={alert_delivery_boy}'
                return HttpResponseRedirect(redirect_url)
            
        condition = wants_delivery == '1' and order_taken_on == "OnCounter" and order_status == "Completed"
        print(f'Condition::{condition}')            
        #if ((order_status == "Out for Delivery" and order_taken_on == 'App') or (delivery_price != '0.0' and order_taken_on == 'OnCounter' and order_status == "Out for Delivery")) or ((order_status == "Completed" and order_taken_on == 'App') or condition) or order_status == "Processing" or order_status == "Pick Up Done" or order_status== "Reached Store":
        if ((order_status == "Out for Delivery" and order_taken_on == 'App') or (wants_delivery == '1' and order_taken_on == 'OnCounter' and order_status == "Out for Delivery")):   
            print('Entering Here Now to send notification to delivery boy')
            #To Send for Delivery Boy
            if order_status !="Processing":
                title = "VFF Group"
                msg = "Delivery Package is ready pick it up from store"
                if order_status == "Completed":
                    title = "Order Completed"
                    msg = "Laundry Package Delivery Successfully. Now You are free to accept new Orders"
                # elif order_status == "Processing":
                #     msg = "Processing has been started for Order ID : #"+str(order_id)+". You are now free to recieve new orders."
                elif order_status == "Pick Up Done":
                    title = "Pick Up Done"
                    msg = "Laundry PickUp Done for Order ID : #"+str(order_id)+""
                elif order_status == "Reached Store":
                    title = "Reached Store"
                    msg = "Now you are ready to Receive New Orders."
                else:
                    msg = "Order ID #"+str(order_id)+" Assigned.\nDelivery Package is ready pick it up from store"

                data = {

                     'order_id_pickup':order_id
                     }
                notifyDeliveryBoy,deliveryBoyID,deliveryBOYName = send_notification_to_delivery_boy(order_id,title,msg,data,order_status,delivery_boy_id_default)
                print(f'deliveryBoyID::{deliveryBoyID}')
                print(f"notifyDeliveryBoy::{notifyDeliveryBoy}")
                

                if (order_status == "Out for Delivery" and deliveryBoyID != '-1' ):
                    try:
                        with connection.cursor() as cursor:
                            filter = ""

                            if order_status == "Out for Delivery" and deliveryBoyID != '-1':
                                filter = ",delivery_boyid='"+str(deliveryBoyID)+"'"
                            query = "update vff.laundry_ordertbl set order_status='"+str(order_status)+"',order_completed='"+str(order_completed)+"'"+filter+" where orderid='"+str(order_id)+"'"
                            print(f'Updating To Busy Status::{query}')
                            cursor.execute(query)
                            connection.commit()
                            
                            #Insert While Assigning Order for delivery
                            query_assign = "insert into vff.laundry_order_assignmenttbl (booking_id,order_id,delivery_boy_id,type_of_order) values ('"+str(booking_id)+"','"+str(order_id)+"','"+str(deliveryBoyID)+"','Drop')"
                            print(f'Inserting Assing to Drop::{query_assign}')
                            cursor.execute(query_assign)
                            connection.commit()
                            
                            #Make Him In Busy Mode
                            query3="update vff.laundry_delivery_boytbl set status='Busy' where delivery_boy_id='"+str(deliveryBoyID)+"'"
                            cursor.execute(query3)
                            print(f'Putting Delivery Boy to busy mode::{query3}')
                            connection.commit()
                    except Exception as e:
                        print(e)
                else:
                    print('No Delivery Boy is Available to Take Orders')
                    alert_delivery_boy = "No Delivery Boy is Free To Receive Orders"
                    redirect_url = reverse('dashboard_app:view_order_detail', kwargs={'orderid': order_id})
                    redirect_url += f'?no_delivery={alert_delivery_boy}'
                    return HttpResponseRedirect(redirect_url)
                    #redirect(reverse('dashboard_app:view_order_detail', kwargs={'orderid': order_id}))
            
            if order_status == "Out for Delivery" and deliveryBoyID != '-1':
                
                jfilter = "" 
                status = ""
                if order_status == "Out for Delivery":
                    jfilter =",delivery_boyid"
                    status = "Busy"
                else:
                    jfilter = ",delivery_boy_id"
                    status = "Free"
                query_token = "select usrname,mobile_no,device_token"+jfilter+" from vff.usertbl,vff.laundry_delivery_boytbl,vff.laundry_ordertbl where usertbl.usrid=laundry_delivery_boytbl.usrid and laundry_ordertbl.delivery_boyid=vff.laundry_delivery_boytbl.delivery_boy_id and orderid='"+str(order_id)+"'"
                result = execute_raw_query_fetch_one(query_token)
                if result:  
                    usrname = result[0] 
                    delivery_boy_id = result[3]
                    device_token = result[2]
                    
                    try:
                        with connection.cursor() as cursor:
                            update_free = "update vff.laundry_delivery_boytbl set status='"+str(status)+"' where delivery_boy_id='"+str(delivery_boy_id)+"'"
                            cursor.execute(update_free)
                            connection.commit()

                    except Exception as e:
                        print(f"Error loading data: {e}")
                
            
        #To send to customer
        title = "VFF Group"
        if order_status == "Completed":
            title = "Order Completed"
            msg = "Laundry Package Delivery Successfully for Order ID : #"+str(order_id)+" . Keep Ordering with Velvet Wash"
        elif order_status == "Processing":
            title = "Processing Status"
            msg = "Processing has been started for your Order ID : #"+str(order_id)+""
        elif order_status == "Pick Up Done":
            title = "Pick Up Done"
            msg = "Laundry PickUp Done for Order ID : #"+str(order_id)+""
        elif order_status == "Reached Store":
            title = "Reached Store"
            msg = "Your Laundry has arrived at Store for Order ID : #"+str(order_id)+".\nWe will ping you once the processing has been started Thank you."
        elif order_status == "Ready for Delivery":
            title = "Ready For Delivery"
            msg = "Your Laundry Package is Ready For Delivery for Order ID : #"+str(order_id)+".\nThank you."
        else:
            msg = "Your Laundry Package is on its way to deliver for Order ID : #"+str(order_id)+""
        data = {
             'intent':'MainRoute',
             }
        notifyCustomer,customerid = send_notification_customer(order_id,title,msg,data)
        
        
        try:
            with connection.cursor() as cursor:
                filter = ""
                if order_status == "Completed":
                    current_timestamp = time.time()
                    current_datetime = datetime.now().strftime("%Y-%m-%d")
                    filter = ",delivery='"+str(current_datetime)+"',delivery_epoch='"+str(current_timestamp)+"'"
                if order_status == "Out for Delivery" and deliveryBoyID != '-1':
                    filter = ",delivery_boyid='"+str(delivery_boy_id)+"'"
                query = "update vff.laundry_ordertbl set order_status='"+str(order_status)+"',order_completed='"+str(order_completed)+"'"+filter+" where orderid='"+str(order_id)+"'"
                print(f'----------------------------------- Updating Order ID with delivery Epoch ----------------')
                print(f'query_update::{query}')
                cursor.execute(query)
                connection.commit()
                query2 = "insert into vff.laundry_order_historytbl(order_id,order_stages) values ('"+str(order_id)+"','"+str(order_status)+"')"
                cursor.execute(query2)
                connection.commit()
                #Insert Delivery Boy Record
                if order_status != "Processing" and order_status !="Ready for Delivery":
                    insert_notify="insert into vff.laundry_notificationtbl(title,body,reciever_id,sender_id,order_id) values ('"+str(title)+"','"+str(msg)+"','"+str(delivery_boy_id)+"','"+str(userid)+"','"+str(order_id)+"')"
                    cursor.execute(insert_notify)
                    print(f'Notification inserted for Delivery Boy::{insert_notify}')
                    connection.commit()
                #Insert Customers Record
                cinsert_notify="insert into vff.laundry_notificationtbl(title,body,reciever_id,sender_id,order_id) values ('"+str(title)+"','"+str(msg)+"','"+str(customerid)+"','"+str(userid)+"','"+str(order_id)+"')"
                cursor.execute(cinsert_notify)
                connection.commit()
                print(f'Notification inserted for Customers::{cinsert_notify}')
                print("Order Status Updated Successfully")
                return redirect(reverse('dashboard_app:view_order_detail', kwargs={'orderid': order_id}))
        except Exception as e:
                print(f"Error loading data: {e}")
            
                
        else:
            #Only when Delivery boy is not needed to update status
            
            try:
                with connection.cursor() as cursor:
                    query2 = "insert into vff.laundry_order_historytbl(order_id,order_stages) values ('"+str(order_id)+"','"+str(order_status)+"')"
                    cursor.execute(query2)
                    connection.commit()
                    query = "update vff.laundry_ordertbl set order_status='"+str(order_status)+"',order_completed='"+str(order_completed)+"' where orderid='"+str(order_id)+"'"    
                    print(f'query_update::{query}')
                    cursor.execute(query)
                    connection.commit()
                    #Insert Customers Record
                    cinsert_notify="insert into vff.laundry_notificationtbl(title,body,reciever_id,sender_id,order_id) values ('"+str(title)+"','"+str(msg)+"','"+str(customerid)+"','"+str(userid)+"','"+str(order_id)+"')"
                    cursor.execute(cinsert_notify)
                    connection.commit()
                    print("Order Status Updated Successfully")
            except Exception as e:
                    print(f"Error loading data: {e}")
                   
    return redirect(reverse('dashboard_app:view_order_detail', kwargs={'orderid': order_id}))

#Get New Notifications for today
def check_notifications(request):
    branch_id = request.session.get('branchid')
    today_date = datetime.now().strftime("%Y-%m-%d")
    print(today_date)
    
    # query = "select notification_id,title,body,date,laundry_notificationtbl.epoch,order_id,booking_id,customer_name,profile_img from vff.laundry_customertbl,vff.laundry_notificationtbl,vff.usertbl where laundry_notificationtbl.sender_id=laundry_customertbl.usrid and laundry_customertbl.usrid=usertbl.usrid and laundry_notificationtbl.date='"+str(today_date)+"' and laundry_notificationtbl.branch_id='"+str(branch_id)+"' and title='Pickup Request' and reciever_id='-1'  order by notification_id desc" #and title='Pickup Request' 
    query="select bookingid,laundry_order_bookingtbl.address,laundry_order_bookingtbl.city,laundry_order_bookingtbl.pincode,laundry_order_bookingtbl.landmark,time_at,customer_name,profile_img from vff.laundry_customertbl,vff.laundry_order_bookingtbl,vff.usertbl where laundry_order_bookingtbl.customerid=laundry_customertbl.consmrid and laundry_customertbl.usrid=usertbl.usrid and booking_status='NA' and booking_date='"+str(today_date)+"' and branch_id='"+str(branch_id)+"' and booking_status='NA' and delivery_boy_id='-1' order by bookingid desc"
    
    query_result = execute_raw_query(query)
    print(f'query_result:::{query_result}')
    
        
    data = []
    sub_items = []    
    if not query_result == 500:
        for row in query_result:
            
            #bookingEpoch = epochToDateTime(depoch)
            data.append({
                'bookingid': row[0],
                'address': row[1],
                'city': row[2],
                'pincode': row[3],
                'landmark': row[4],
                'booking_done_timing': row[5],
                'customer_name': row[6],
                'customer_profile': row[7],   
            })    
    else:
        error_msg = 'Something Went Wrong'
        
    
    
    context ={'query_result':data}
    
    
    return JsonResponse(context)


#Get New Notifications for today
def get_todays_notification(request):
    branch_id = request.session.get('branchid')
    today_date = datetime.now().strftime("%Y-%m-%d")
    print(today_date)
    query = "select notification_id,title,body,date,laundry_notificationtbl.epoch,order_id,booking_id,name as delivery_boy_name,customer_name,profile_img from vff.laundry_customertbl,vff.laundry_delivery_boytbl,vff.laundry_notificationtbl,vff.usertbl where laundry_notificationtbl.sender_id=laundry_customertbl.usrid and laundry_delivery_boytbl.delivery_boy_id=laundry_notificationtbl.reciever_id and laundry_customertbl.usrid=usertbl.usrid and laundry_notificationtbl.date='"+str(today_date)+"' and laundry_notificationtbl.branch_id='"+str(branch_id)+"' and title='Pickup Request'  order by notification_id desc" #and title='Pickup Request' 
    
    query_result = execute_raw_query(query)
    print(f'query_result:::{query_result}')
    
        
    data = []
    sub_items = []    
    if not query_result == 500:
        for row in query_result:
            
            data.append({
                'notification_id': row[0],
                'title': row[1],
                'body': row[2],
                'date': row[3],
                'epoch': row[4],
                'order_id': row[5],
                'booking_id': row[6],
                'delivery_boy_name': row[7],
                'customer_name': row[8],
                'customer_profile': row[9],
                
               
            })    
    else:
        error_msg = 'Something Went Wrong'
        
    #select notification_id,title,body,date,laundry_notificationtbl.epoch,order_id,booking_id,customer_name,profile_img from vff.laundry_customertbl,vff.laundry_notificationtbl,vff.usertbl where laundry_notificationtbl.sender_id=laundry_customertbl.usrid and laundry_notificationtbl.reciever_id='-1' and laundry_customertbl.usrid=usertbl.usrid and laundry_notificationtbl.date='2023-11-10' and laundry_notificationtbl.branch_id='1' order by notification_id desc
    
    context ={'query_result':data}
    
    
    return JsonResponse(context)
    
#To Print Label Tags
def print_label_tags(request,orderid):
    query = "select consmrid,usertbl.usrid,customer_name,mobile_no,houseno,address,city,pincode,landmark,profile_img,device_token,orderid,delivery_boyid,quantity,price,pickup_dt,delivery,clat,clng,order_completed,order_status,additional_instruction,laundry_ordertbl.epoch,cancel_reason,feedback,delivery_epoch,name as deliveryboy_name,categoryid,subcategoryid,booking_type,dt,cat_img,cat_name,sub_cat_name,sub_cat_img,actual_cost,time,item_cost,item_quantity,type,section_type,laundry_ordertbl.booking_id,gstamount,igstamount,discount_price,wants_delivery from vff.laundry_active_orders_tbl,vff.laundry_ordertbl,vff.laundry_customertbl,vff.usertbl,vff.laundry_delivery_boytbl where laundry_customertbl.usrid=usertbl.usrid and laundry_ordertbl.customerid=laundry_customertbl.consmrid and laundry_ordertbl.delivery_boyid=laundry_delivery_boytbl.delivery_boy_id and laundry_active_orders_tbl.order_id=laundry_ordertbl.orderid and orderid='"+str(orderid)+"' order by orderid desc;"
    
    query_result = execute_raw_query(query)
    print(f'query_result:::{query_result}')
    
        
    data = []
    sub_items = []    
    if not query_result == 500:
        for row in query_result:
            # quantity = row[38]
            # print(f'quantity:add:{quantity}')
            # quantity_range = list(range(quantity)) 
            depoch = row[25]#delivery epoch
            oepoch = row[22]#order taken epoch
            orderStatus = row[20]
            print("Delivery Epoch:"+str(depoch))
            print("Order Taken Epoch:"+str(oepoch))
            deliveryEpoch = epochToDateTime(depoch)
            orderTakenEpoch = epochToDateTime(oepoch)
            if orderStatus != "Completed":
                deliveryEpoch = "Not Delivered Yet"
            cat_name=row[32]
            if cat_name != 'DRY CLEAN':
                sub_items.append(row[33])
            data.append({
                'consmrid': row[0],
                'usrid': row[1],
                'customer_name': row[2],
                'mobile_no': row[3],
                'houseno': row[4],
                'address': row[5],
                'city': row[6],
                'pincode': row[7],
                'landmark': row[8],
                'profile_img': row[9],
                'device_token': row[10],
                'orderid': row[11],
                'delivery_boyid': row[12],
                'quantity':row[13],
                'price': row[14],
                'pickup_dt': row[15],
                'delivery_dt': row[16],
                'clat': row[17],
                'clng': row[18],
                'order_completed': row[19],
                'order_status': orderStatus,
                'additional_instruction': row[21],
                'order_taken_epoch': orderTakenEpoch,
                'cancel_reason': row[23],
                'feedback': row[24],
                'delivery_epoch': deliveryEpoch,
                'delivery_boy_name': row[26],
                'categoryid': row[27],
                'subcategoryid': row[28],
                'ordertype': row[29],
                'dt': row[30],
                'cat_img': row[31],
                'cat_name': row[32],
                'sub_cat_name': row[33],
                'sub_cat_img': row[34],
                'actual_cost': row[35],
                'time': row[36],
                'item_cost': row[37],
                'item_quantity': row[38],
                'type_of': row[39],
                'section_type': row[40],
                'booking_id': row[41],
                'gstamount': row[42],
                'igstamount': row[43],
                'discount_price': row[44],
                'wants_delivery': row[45],
                
                
                
               
            })
        
        #Payment Details
        payment_id = 'Payment Not Done'
        query_payment = "select razor_pay_payment_id,status,time,dt,payment_type from vff.laundry_payment_tbl where order_id='"+str(orderid)+"'"
        pay_result = execute_raw_query_fetch_one(query_payment)
        if pay_result:   
            payment_id = pay_result[0]
            payment_type = pay_result[4]
        
        
        #extra_cart_item like softner
        extra_error = "No Extra Items added"
        extra_query = "select extra_item_name,price from vff.laundry_cart_extra_items_tbl where order_id='"+str(orderid)+"'"
        extra_query_result = execute_raw_query(extra_query)
        extra_data = []    
        if not extra_query_result == 500:
            for row in extra_query_result:
                extra_data.append({
                    'extra_item_name':row[0],
                    'extra_item_price':row[1]
                })
        #delivery charges
        delivery_price = 0
        total_laundry_cost = 0
        range_price = 0
        delivery_query = "select price,range  from vff.laundry_delivery_chargetbl"
        dlvrych_result = execute_raw_query_fetch_one(delivery_query)
        if dlvrych_result:   
            delivery_price = dlvrych_result[0]
            range_price = dlvrych_result[1]
        
        extra_item_sum = sum(extra['extra_item_price'] for extra in extra_data)

        total_laundry_cost = sum(item['item_cost'] for item in data)
        print(f'total_laundry_cost::{total_laundry_cost}')
        print(f'extra_item_sum::{extra_item_sum}')
        print(f'delivery_price::{delivery_price}')
        
        if total_laundry_cost != 0:
            if total_laundry_cost < range_price:
                total_laundry_cost += delivery_price
                print(f'Updating TotalCost:{total_laundry_cost}')
            else:
                delivery_price = 0
        
        #request.session['branchid'] = branchid
        branch_name = request.session.get('branch_name') 
        branch_address = request.session.get('branch_address') 
        branch_gstno = request.session.get('branch_gstno')
        branch_igstno = request.session.get('branch_igstno')
        branch_city = request.session.get('branch_city')
        branch_state = request.session.get('branch_state')
        branch_pincode = request.session.get('branch_pincode')
        branch_contactno = request.session.get('branch_contactno')
        branch_admin_name = request.session.get('branch_admin_name')
        branch_admin_id = request.session.get('branch_admin_id')
        branchid = request.session.get('branchid')
        
        
        total_cost = total_laundry_cost + extra_item_sum
        print(f'total_cost::{total_cost}')
        totalGST = (total_cost * 18) / 100
        print(f'totalGST::{totalGST}')
        gst_amount = totalGST
        sub_total = total_laundry_cost
        
        first_order_id = data[0]['orderid'] if data else ''
        discount_amount = data[0]['discount_price'] if data else ''
        booking_id = data[0]['booking_id'] if data else ''
        mobile_no = data[0]['mobile_no'] if data else ''
        customer_name = data[0]['customer_name'] if data else ''
        address = data[0]['address'] if data else ''
        houseno = data[0]['houseno'] if data else ''
        city = data[0]['city'] if data else ''
        pincode = data[0]['pincode'] if data else ''
        landmark = data[0]['landmark'] if data else ''
        order_status = data[0]['order_status'] if data else ''
        order_completed = data[0]['order_completed'] if data else ''
        order_date = data[0]['order_taken_epoch'] if data else ''
        delivery_date = data[0]['delivery_epoch'] if data else ''
        wants_delivery = data[0]['wants_delivery'] if data else ''
        request.session['order_id'] = first_order_id
        order_completed_status = ""
        if order_completed == 0:
            order_completed_status = "Accepted"
        elif order_completed == 1:
            order_completed_status = "Completed"
        elif order_completed_status == 2:
            order_completed_status = "Cancelled"
            
        print(f'OrderID::{first_order_id}')
        print(f'sub_items:::{sub_items}')
        # Extract numbers within parentheses and sum them up
        total_sum = sum(int(re.search(r'\((\d+)\)', item).group(1)) for item in sub_items if re.search(r'\((\d+)\)', item))
        print(f'total_sum::{total_sum}')
        
        receiptID = ''
        receiptName = ''
        branchID = ''
        receiptDate = ''
        #Insert Record in Receipt Table
        receipt_query = "select receiptid,receipt_name,branch_id,date  from vff.laundry_receipt_invoice_tbl where order_id='"+str(first_order_id)+"'"
        receipt_result = execute_raw_query_fetch_one(receipt_query)
        if receipt_result:   
            receiptID = receipt_result[0]
            receiptName = receipt_result[1]
            branchID = receipt_result[2]
            receiptDate = receipt_result[3]
            
        else:
            try:
                with connection.cursor() as cursor:
                    insert_receipt="insert into vff.laundry_receipt_invoice_tbl (order_id,receipt_name,receipt_id,branch_id) values ('"+str(first_order_id)+"','"+str(branch_admin_name)+"','"+str(branch_admin_id)+"','"+str(branchid)+"')  returning receiptid"
                    cursor.execute(insert_receipt)
                    print(f'Insert receipt record:{insert_receipt}')
                    receipt_id = cursor.fetchone()[0]  
                    receiptID = receipt_id
                    receipt_query = "select receiptid,receipt_name,branch_id,date  from vff.laundry_receipt_invoice_tbl where order_id='"+str(first_order_id)+"'"
                    receipt_result = execute_raw_query_fetch_one(receipt_query)
                    if receipt_result:   
                        receiptID = receipt_result[0]
                        receiptName = receipt_result[1]
                        branchID = receipt_result[2]
                        receiptDate = receipt_result[3]
        
            except Exception as e:
                print(e)
                receipt_query = "select receiptid,receipt_name,branch_id,date  from vff.laundry_receipt_invoice_tbl where order_id='"+str(first_order_id)+"'"
                receipt_result = execute_raw_query_fetch_one(receipt_query)
                if receipt_result:   
                    receiptID = receipt_result[0]
                    receiptName = receipt_result[1]
                    branchID = receipt_result[2]
                    receiptDate = receipt_result[3]
            
            
                
            
        
        
    else:
        error_msg = 'Something Went Wrong'
    
    context ={'query_result':data,'extra_data':extra_data,'payment_id':payment_id,'order_id':first_order_id,'customer_name':customer_name
              ,'address':address,'houseno':houseno,'city':city,'pincode':pincode,'landmark':landmark,'order_status':order_status,'order_completed_status':order_completed_status,'order_date':order_date,'delivery_date':delivery_date,'extra_item_sum':extra_item_sum,'delivery_price':delivery_price,'total_cost':total_cost,'extra_error':extra_error,'range_price':range_price,'sub_items':sub_items,'booking_id':booking_id,'mobile_no':mobile_no,'branch_address':branch_address,'branch_name':branch_name,'branch_gstno':branch_gstno,'branch_igstno':branch_igstno,'branch_city':branch_city,'branch_state':branch_state,'branch_pincode':branch_pincode,'branch_contactno':branch_contactno,'payment_type':payment_type,'gst_amount':gst_amount,'discount_amount':discount_amount,'sub_total':sub_total,'receipt_id':receiptID,'branch_id':branchID,'receiptName':receiptName,'receiptDate':receiptDate,'wants_delivery':wants_delivery}
    
    return render(request,'invoice_pages/print_tag_labels.html',context)        
        
#Thermal Printer size
def generate_bill(request, orderid):
    query = "select consmrid,usertbl.usrid,customer_name,mobile_no,houseno,address,city,pincode,landmark,profile_img,device_token,orderid,delivery_boyid,quantity,price,pickup_dt,delivery,clat,clng,order_completed,order_status,additional_instruction,laundry_ordertbl.epoch,cancel_reason,feedback,delivery_epoch,name as deliveryboy_name,categoryid,subcategoryid,booking_type,dt,cat_img,cat_name,sub_cat_name,sub_cat_img,actual_cost,time,item_cost,item_quantity,type,section_type,laundry_ordertbl.booking_id,gstamount,igstamount,discount_price,wants_delivery from vff.laundry_active_orders_tbl,vff.laundry_ordertbl,vff.laundry_customertbl,vff.usertbl,vff.laundry_delivery_boytbl where laundry_customertbl.usrid=usertbl.usrid and laundry_ordertbl.customerid=laundry_customertbl.consmrid and laundry_ordertbl.delivery_boyid=laundry_delivery_boytbl.delivery_boy_id and laundry_active_orders_tbl.order_id=laundry_ordertbl.orderid and orderid='"+str(orderid)+"' order by orderid desc;"
    
    query_result = execute_raw_query(query)
    print(f'query_result:::{query_result}')
    
        
    data = []
    sub_items = []    
    if not query_result == 500:
        for row in query_result:
            depoch = row[25]#delivery epoch
            oepoch = row[22]#order taken epoch
            orderStatus = row[20]
            item_cost_str = row[37]
            item_cost = float(item_cost_str)
            formatted_cost = '{:.2f}'.format(item_cost)
            print("Delivery Epoch:"+str(depoch))
            print("Order Taken Epoch:"+str(oepoch))
            deliveryEpoch = epochToDateTime(depoch)
            orderTakenEpoch = epochToDateTime(oepoch)
            if orderStatus != "Completed":
                deliveryEpoch = "Not Delivered Yet"
            cat_name=row[32]
            if cat_name != 'DRY CLEAN':
                sub_items.append(row[33])
            data.append({
                'consmrid': row[0],
                'usrid': row[1],
                'customer_name': row[2],
                'mobile_no': row[3],
                'houseno': row[4],
                'address': row[5],
                'city': row[6],
                'pincode': row[7],
                'landmark': row[8],
                'profile_img': row[9],
                'device_token': row[10],
                'orderid': row[11],
                'delivery_boyid': row[12],
                'quantity':row[13],
                'price': row[14],
                'pickup_dt': row[15],
                'delivery_dt': row[16],
                'clat': row[17],
                'clng': row[18],
                'order_completed': row[19],
                'order_status': orderStatus,
                'additional_instruction': row[21],
                'order_taken_epoch': orderTakenEpoch,
                'cancel_reason': row[23],
                'feedback': row[24],
                'delivery_epoch': deliveryEpoch,
                'delivery_boy_name': row[26],
                'categoryid': row[27],
                'subcategoryid': row[28],
                'ordertype': row[29],
                'dt': row[30],
                'cat_img': row[31],
                'cat_name': row[32],
                'sub_cat_name': row[33],
                'sub_cat_img': row[34],
                'actual_cost': row[35],
                'time': row[36],
                'item_cost': formatted_cost,
                'item_quantity': row[38],
                'type_of': row[39],
                'section_type': row[40],
                'booking_id': row[41],
                'gstamount': row[42],
                'igstamount': row[43],
                'discount_price': row[44],
                'wants_delivery': row[45],
                
                
                
               
            })
        
        #Payment Details
        payment_id = 'Payment Not Done'
        query_payment = "select razor_pay_payment_id,status,time,dt,payment_type from vff.laundry_payment_tbl where order_id='"+str(orderid)+"'"
        pay_result = execute_raw_query_fetch_one(query_payment)
        if pay_result:   
            payment_id = pay_result[0]
            payment_type = pay_result[4]
        
        
        #extra_cart_item like softner
        extra_error = "No Extra Items added"
        extra_query = "select extra_item_name,price from vff.laundry_cart_extra_items_tbl where order_id='"+str(orderid)+"'"
        extra_query_result = execute_raw_query(extra_query)
        extra_data = []    
        if not extra_query_result == 500:
            for row in extra_query_result:
                extra_data.append({
                    'extra_item_name':row[0],
                    'extra_item_price':row[1]
                })
        #delivery charges
        delivery_price = 0
        total_laundry_cost = 0
        range_price = 0
        delivery_query = "select price,range  from vff.laundry_delivery_chargetbl"
        dlvrych_result = execute_raw_query_fetch_one(delivery_query)
        if dlvrych_result:   
            delivery_price = dlvrych_result[0]
            range_price = dlvrych_result[1]
        
        extra_item_sum = sum(extra['extra_item_price'] for extra in extra_data)

        # total_laundry_cost = sum(item['item_cost'] for item in data)
        total_laundry_cost = sum(round(float(item['item_cost']), 2) for item in data)
        print(f'total_laundry_cost::{total_laundry_cost}')
        print(f'extra_item_sum::{extra_item_sum}')
        print(f'delivery_price::{delivery_price}')
        
        # if total_laundry_cost != 0:
        #     if total_laundry_cost < range_price:
        #         total_laundry_cost += delivery_price
        #         print(f'Updating TotalCost:{total_laundry_cost}')
        #     else:
        #         delivery_price = 0
        
        #request.session['branchid'] = branchid
        branch_name = request.session.get('branch_name') 
        branch_address = request.session.get('branch_address') 
        branch_gstno = request.session.get('branch_gstno')
        branch_igstno = request.session.get('branch_igstno')
        branch_city = request.session.get('branch_city')
        branch_state = request.session.get('branch_state')
        branch_pincode = request.session.get('branch_pincode')
        branch_contactno = request.session.get('branch_contactno')
        branch_admin_name = request.session.get('branch_admin_name')
        branch_admin_id = request.session.get('branch_admin_id')
        branchid = request.session.get('branchid')
        
        
        total_cost = total_laundry_cost + extra_item_sum
        
        
        sub_total = total_laundry_cost
        gstamount = data[0]['gstamount'] if data else ''
        igstamount = data[0]['igstamount'] if data else ''
        state_gst = 0
        central_gst = 0
        gst_amount = '0'
        print(f'igstamount:::{igstamount}')
        print(f'gstamount:::{gstamount}')
        if gstamount != 0 and gstamount != 0.0 :
            totalGST = (total_cost * 18) / 100
            print(f'totalGST::{totalGST}')
            state_gst = gstamount / 2
            central_gst = gstamount / 2
            gst_amount = gstamount
            if total_cost < range_price:
                total_cost += gstamount + delivery_price
            else:
                total_cost += gstamount
                delivery_price = 0
        else:
            if total_cost < range_price:
                total_cost += igstamount + delivery_price
            else:
                total_cost += igstamount 
                delivery_price = 0
        igstamount = round(igstamount,2)
        if igstamount == 0.0:
            igstamount = '0.0'
        
        print(f'total_cost::{total_cost}')
        first_order_id = data[0]['orderid'] if data else ''
        discount_amount = data[0]['discount_price'] if data else ''
        delivery_dt = data[0]['delivery_dt'] if data else ''
        booking_id = data[0]['booking_id'] if data else ''
        mobile_no = data[0]['mobile_no'] if data else ''
        customer_name = data[0]['customer_name'] if data else ''
        address = data[0]['address'] if data else ''
        houseno = data[0]['houseno'] if data else ''
        city = data[0]['city'] if data else ''
        pincode = data[0]['pincode'] if data else ''
        landmark = data[0]['landmark'] if data else ''
        order_status = data[0]['order_status'] if data else ''
        order_completed = data[0]['order_completed'] if data else ''
        order_date = data[0]['order_taken_epoch'] if data else ''
        delivery_date = data[0]['delivery_epoch'] if data else ''
        wants_delivery = data[0]['wants_delivery'] if data else ''
        request.session['order_id'] = first_order_id
        order_completed_status = ""
        if order_completed == 0:
            order_completed_status = "Accepted"
        elif order_completed == 1:
            order_completed_status = "Completed"
        elif order_completed_status == 2:
            order_completed_status = "Cancelled"
            
        print(f'OrderID::{first_order_id}')
        print(f'sub_items:::{sub_items}')
        receiptID = ''
        receiptName = ''
        branchID = ''
        receiptDate = ''
        #Insert Record in Receipt Table
        receipt_query = "select receiptid,receipt_name,branch_id,date  from vff.laundry_receipt_invoice_tbl where order_id='"+str(first_order_id)+"'"
        receipt_result = execute_raw_query_fetch_one(receipt_query)
        if receipt_result:   
            receiptID = receipt_result[0]
            receiptName = receipt_result[1]
            branchID = receipt_result[2]
            receiptDate = receipt_result[3]
            
        else:
            try:
                with connection.cursor() as cursor:
                    insert_receipt="insert into vff.laundry_receipt_invoice_tbl (order_id,receipt_name,receipt_id,branch_id) values ('"+str(first_order_id)+"','"+str(branch_admin_name)+"','"+str(branch_admin_id)+"','"+str(branchid)+"')  returning receiptid"
                    cursor.execute(insert_receipt)
                    print(f'Insert receipt record:{insert_receipt}')
                    receipt_id = cursor.fetchone()[0]  
                    receiptID = receipt_id
                    receipt_query = "select receiptid,receipt_name,branch_id,date  from vff.laundry_receipt_invoice_tbl where order_id='"+str(first_order_id)+"'"
                    receipt_result = execute_raw_query_fetch_one(receipt_query)
                    if receipt_result:   
                        receiptID = receipt_result[0]
                        receiptName = receipt_result[1]
                        branchID = receipt_result[2]
                        receiptDate = receipt_result[3]
        
            except Exception as e:
                print(e)
                receipt_query = "select receiptid,receipt_name,branch_id,date  from vff.laundry_receipt_invoice_tbl where order_id='"+str(first_order_id)+"'"
                receipt_result = execute_raw_query_fetch_one(receipt_query)
                if receipt_result:   
                    receiptID = receipt_result[0]
                    receiptName = receipt_result[1]
                    branchID = receipt_result[2]
                    receiptDate = receipt_result[3]
            
            
                
            
        
        
    else:
        error_msg = 'Something Went Wrong'
    
    context ={'query_result':data,'extra_data':extra_data,'payment_id':payment_id,'order_id':first_order_id,'customer_name':customer_name
              ,'address':address,'houseno':houseno,'city':city,'pincode':pincode,'landmark':landmark,'order_status':order_status,'order_completed_status':order_completed_status,'order_date':order_date,'delivery_date':delivery_date,'extra_item_sum':extra_item_sum,'delivery_price':delivery_price,'total_cost':round(total_cost,2),'extra_error':extra_error,'range_price':range_price,'sub_items':sub_items,'booking_id':booking_id,'mobile_no':mobile_no,'branch_address':branch_address,'branch_name':branch_name,'branch_gstno':branch_gstno,'branch_igstno':branch_igstno,'branch_city':branch_city,'branch_state':branch_state,'branch_pincode':branch_pincode,'branch_contactno':branch_contactno,'payment_type':payment_type,'gst_amount':gst_amount,'discount_amount':round(discount_amount,2),'sub_total':round(sub_total,2),'receipt_id':receiptID,'branch_id':branchID,'receiptName':receiptName,'receiptDate':receiptDate,'wants_delivery':wants_delivery,'delivery_dt':delivery_dt,'state_gst':round(state_gst, 2),'central_gst':round(central_gst,2),'igstamount':igstamount}
    
    # return HttpResponse(formatted_bill_content)
    return render(request,'invoice_pages/receipt_bill.html',context)

import textwrap

def fit_to_thermal_printer_paper(bill_content):
  """Fits the given bill content string to thermal printer paper.

  Args:
    bill_content: A string containing the bill content.

  Returns:
    A string containing the bill content, wrapped to the maximum line width and
    with formatting characters to control the text size and other options.
  """

  # Calculate the maximum line width.
  max_line_width = 40

  # Wrap the bill content string to the maximum line width.
  wrapped_bill_content = textwrap.wrap(bill_content, max_line_width)

  # Insert formatting characters to control the text size and other options.
  formatted_bill_content = ""
  for line in wrapped_bill_content:
    formatted_bill_content += line + "\n"

    # Set the text size to double-height and double-width for the "Total Amount" line.
    if line.startswith("Total Amount"):
      formatted_bill_content += "\x1B\x21\x10"

      # Reset the text size to normal after the "Total Amount" line.
    elif line.startswith("Terms and Conditions"):
      formatted_bill_content += "\x1B\x21\x01"

      # Reset the text size to normal after the "Terms and Conditions" section.
    formatted_bill_content += "\x1B\x21\x00"

  return formatted_bill_content

# Example usage:
#formatted_bill_content = fit_to_thermal_printer_paper(bill_content)

# Print or store the formatted_bill_content string as needed.

#All Main Branches Details
def all_main_branches(request):
    isLogin = is_loggedin(request)
    if isLogin == False:
        return redirect('dashboard_app:login')
    error_msg = "No Branches Created Till Now"
    branch_id = request.session.get('branchid')
    owner_id = request.session.get('userid')
    filter = ''
    super_admin = request.session.get('username')
    if branch_id and super_admin!='Super Admin':
        filter = "and branchtbl.owner_id='"+str(owner_id)+"'"
    
    query = "select branchid,branch_name,owner_name,branchtbl.address,branch_type,creation_date,branchtbl.epoch,status,branchtbl.city,branchtbl.state,mobile_no,usertbl.address,usertbl.city,usertbl.pincode,branchtbl.pincode,profile_img,device_token,owner_id from vff.usertbl,vff.branchtbl where branchtbl.owner_id=usertbl.usrid "+filter+""
    #select admintbl.branchid,branch_name,owner_name,branchtbl.address,branch_type,creation_date,branchtbl.epoch,branchtbl.status,branchtbl.city,branchtbl.state,mobile_no,usertbl.address,usertbl.city,usertbl.pincode,branchtbl.pincode,profile_img,device_token,owner_id from vff.admintbl,vff.usertbl,vff.branchtbl where branchtbl.owner_id=usertbl.usrid and admintbl.usrid=usertbl.usrid and admintbl.usrid=branchtbl.owner_id and admintbl.branchid!='-1'  and admintbl.usrid='"+str(admin_usrid)+"'
    query_result = execute_raw_query(query)
    
    
        
    data = []    
    if not query_result == 500:
        for row in query_result:
            
            data.append({
                'branchid': row[0],
                'branch_name': row[1],
                'owner_name': row[2],
                'branch_address': row[3],
                'branch_type': row[4],
                'branch_creation_date': row[5],
                'branch_epoch': row[6],
                'branch_status': row[7],
                'branch_city': row[8],
                'branch_state': row[9],
                'mobile_no': row[10],
                'address': row[11],
                'city': row[12],
                'pincode': row[13],
                'branch_pincode': row[14],
                'profile_img': row[15],
                'device_token': row[16],
                'owner_id': row[17],
                
               
            })
    else:
        error_msg = 'Something Went Wrong'
    current_url = request.get_full_path()
    # using the 'current_url' variable to determine the active card.
    context = {'query_result': data,'current_url': current_url,'error_msg':error_msg}
    
    return render(request, 'branch_pages/all_main_branches.html', context)

#Add New Branch
def add_new_branch(request,branch_id=None,usr_id=None):
    
    isLogin = is_loggedin(request)
    if isLogin == False:
        return redirect('dashboard_app:login')
    # If usrid is provided, retrieve the data for the selected Branch Table
    data = {}
    print(branch_id)
    if branch_id:
        try:
            with connection.cursor() as cursor:
                query = "select branch_name,owner_name,branchtbl.address,branch_type,branchtbl.city,branchtbl.state,mobile_no,usertbl.address,usertbl.city,usertbl.pincode,branchtbl.pincode,profile_img,owner_id,aadhar_no,houseno,usertbl.landmark,date_of_birth,age,gender,gstno,igstno,branchtbl.landmark,contactno,state_name from vff.usertbl,vff.branchtbl where branchtbl.owner_id=usertbl.usrid and branchid='"+str(branch_id)+"'"
                cursor.execute(query)
                print(f'Query Branch Edit ::{query}')
                row = cursor.fetchone()
                
                print(f'fetching the single user data::{row}')
                if row:
                    image_url = row[11]
                    data = {
                        'branchid': branch_id,
                        'branch_name': row[0],
                        'owner_name': row[1],
                        'branch_address': row[2],
                        'branch_type': row[3],
                        'branch_city': row[4],
                        'branch_state': row[5],
                        'primaryno': row[6],
                        'fulladdress': row[7],
                        'city': row[8],
                        'pincode': row[9],
                        'branch_pincode': row[10],
                        'profile_img': image_url,
                        'owner_id': row[12],
                        'aadhar_no': row[13],
                        'houseno': row[14],
                        'landmark': row[15],
                        'dateofbirth': row[16],
                        'age': row[17],
                        'gender': row[18],
                        'gstno': row[19],
                        'igstno': row[20],
                        'branch_landmark': row[21],
                        'branch_contactno': row[22],
                        'state': row[23],
                        
                        
                        
                        
                    }
        except Exception as e:
            print(f"Error loading data: {e}") 
       
    if request.method == "POST":
        uname = request.POST.get('fullname')
        primary_mobno = request.POST.get('primaryno')
        age = request.POST.get('age')
        gender = request.POST.get('gender')
        address = request.POST.get('fulladdress')
        pincode = request.POST.get('pincode')
        land_mark = request.POST.get('landmark')
        date_of_birth = request.POST.get('dateofbirth')
        queries = request.POST.get('questions')
        gstno = request.POST.get('gstno')
        igstno = request.POST.get('igstno')
        branch_name = request.POST.get('branch_name')
        branch_address = request.POST.get('branch_address')
        branch_state = request.POST.get('branch_state')
        branch_city = request.POST.get('branch_city')
        branch_pincode = request.POST.get('branch_pincode')
        branch_landmark = request.POST.get('branch_landmark')
        branch_contactno = request.POST.get('branch_contactno')
        owner_city = request.POST.get('city')
        owner_state = request.POST.get('state')
        uploaded_image = request.FILES.get('profile-image1')

        print(f'branch_name--->{branch_name}')
        if uploaded_image:
            image_url = upload_images2(uploaded_image)
        elif data.get('profile_img'):
            image_url = data.get('profile_img')
        else:
            # Handle the case where there's no uploaded image and no previous image
            image_url = 'NA'  # Set it to a default value or handle accordingly
            
        # image_url = 'NA'
        # if request.FILES.get('profile-image1'):
        #         uploaded_image = request.FILES['profile-image1']
        #         image_url = upload_images2(uploaded_image)
            

        
        
        if not queries:
            queries = 'No queries'
        if not gstno:
            gstno = "-1"
        if not igstno:
            igstno = "-1"
        
        errors = []
        if not date_of_birth:
            today_date = timezone.now().date() 
            formatted_date = today_date.strftime('%Y-%m-%d')
            date_of_birth = formatted_date
        if not age:
            age = '-1'
        if not land_mark:
            land_mark = 'NA'
        
        
        try:
            with connection.cursor() as cursor:
                if branch_id:
                    print(f'branch_id--->::{branch_id}')
                    # Update an existing branchid
                    update_query = (
                        "update vff.usertbl set usrname='"+str(uname)+"',mobile_no='"+str(primary_mobno)+"',address='"+str(address)+"',age='"+str(age)+"',gender='"+str(gender)+"',date_of_birth='"+str(date_of_birth)+"',pincode='"+str(pincode)+"',landmark='"+str(land_mark)+"',profile_img='"+str(image_url)+"',city='"+str(owner_city)+"',state_name='"+str(owner_state)+"' where usrid='"+str(usr_id)+"'"
                    )
                    print(f"update user details::{update_query}")
                    cursor.execute(update_query)
                    
                    update_customer = (
                        "update vff.branchtbl set branch_name='"+str(branch_name)+"', owner_name='"+str(uname)+"', address='"+str(branch_address)+"', city='"+str(branch_city)+"',state='"+str(branch_state)+"',pincode='"+str(branch_pincode)+"',gstno='"+str(gstno)+"',igstno='"+str(igstno)+"',landmark='"+str(branch_landmark)+"',contactno='"+str(branch_contactno)+"' where branchid='"+str(branch_id)+"'"
                    )
                    print(f"update customer details::{update_customer}")
                    cursor.execute(update_customer)
                else:
                    # Insert a new Branch Owner
                    usertbl_query = "insert into vff.usertbl (usrname,mobile_no,address,age,gender,date_of_birth,pincode,landmark,profile_img,city,state_name) VALUES ('"+str(uname)+"', '"+str(primary_mobno)+"', '"+str(address)+"','"+str(age)+"','"+str(gender)+"','"+str(date_of_birth)+"','"+str(pincode)+"','"+str(land_mark)+"','"+str(image_url)+"','"+str(owner_city)+"','"+str(owner_state)+"') RETURNING usrid"
                    cursor.execute(usertbl_query)
                    usrid = cursor.fetchone()[0]  # Retrieve the returned usrid
                    
                    #Insert Branch Owner + Branch details
                    insert_query = "insert into vff.branchtbl(branch_name,owner_name,owner_id,address,branch_type,city,state,pincode,gstno,igstno,landmark,contactno) values ('"+str(branch_name)+"','"+str(uname)+"','"+str(usrid)+"','"+str(branch_address)+"','Franchise','"+str(branch_city)+"','"+str(branch_state)+"','"+str(branch_pincode)+"','"+str(gstno)+"','"+str(igstno)+"','"+str(branch_landmark)+"','"+str(branch_contactno)+"')"
                    print(f"Create New Branch details::{insert_query}")
                    cursor.execute(insert_query)
                connection.commit()

                print("Branch Details Added/Updated Successfully.")
                return redirect('dashboard_app:all_main_branches')
        except Exception as e:
            print(f"Error loading data: {e}")

    
    
    return render(request,'branch_pages/add_new_branch.html',{'data':data})

#Add Items to Cart
def add_items_to_cart(request):
    
    isLogin = is_loggedin(request)
    if isLogin == False:
        return redirect('dashboard_app:login')
    
    
    error_msg = "Something Went Wrong"
    if request.method == "POST":
        jdict = json.loads(request.body)
        key_pair=jdict['key']
        cat_id = jdict['cat_id']
        customer_id = jdict['customer_id']
        booking_id = jdict['booking_id']
        booking_type = jdict['booking_type']
        cat_img = jdict['cat_img']
        cat_name = jdict['cat_name']
        print(f'given_cat_id:::{cat_id}')
        print(f'booking_id_add_cart:::{booking_id}')
        
                
        print(f"key_pair::{key_pair}")
        if key_pair == 2:
            sub_cat_name = jdict['sub_cat_name']
            item_quantity = jdict['item_quantity']
            actual_cost = jdict['actual_cost']
            cost = jdict['cost']
            type_of = jdict['type_of']
            sub_cat_id = jdict['sub_cat_id']
            sub_cat_img = jdict['sub_cat_img']
            section_type = jdict['section_type']
            
            
            
            try:
                with connection.cursor() as cursor:
                    add_items_cart_query = "insert into vff.laundry_cart_items(catid,subcatid,customer_id,booking_id,booking_type,item_cost,item_quantity,type,cat_img,cat_name,sub_cat_name,sub_cat_img,actual_cost,section_type) values ('"+str(cat_id)+"','"+str(sub_cat_id)+"','"+str(customer_id)+"','"+str(booking_id)+"','"+str(booking_type)+"','"+str(cost)+"','"+str(item_quantity)+"','"+str(type_of)+"','"+str(cat_img)+"','"+str(cat_name)+"','"+str(sub_cat_name)+"','"+str(sub_cat_img)+"','"+str(actual_cost)+"','"+str(section_type)+"')"
                    print(f'add_items_cart Query::{add_items_cart_query}')
                    cursor.execute(add_items_cart_query)
                    connection.commit()
                    
            except Exception as e:
                print(f"Error loading data: {e}")
            #order_accept_tbl = "insert into vff.laundry_delivery_accept_tbl(delivery_boy_id,status,booking_id,branch_id) values ('"+str(delivery_boy_id)+"','"+str(status)+"','"+str(booking_id)+"','"+str(branch_id)+"')"
            ##Order Assignment
            #query5="insert into vff.laundry_order_assignmenttbl(booking_id,delivery_boy_id,type_of_order) values ('"+str(booking_id)+"','"+str(delivery_boy_id)+"','Pickup')"//"Accepted"
        else:
            cat_id = jdict['cat_id']
            customer_id = jdict['customer_id']
            
            booking_type = jdict['booking_type']
            cat_img = jdict['cat_img']
            cat_name = jdict['cat_name']  
            all_data = jdict['all_items']
            print(f'all_data::{all_data}')
            
            try:
                with connection.cursor() as cursor:
                    for item in all_data:
                        print(f'itemss--->{item}')
                        sub_cat_name = item['sub_cat_name']
                        print(f'sub_cat_name::{sub_cat_name}')
                        item_quantity = item['item_quantity']
                        actual_cost = item['actual_cost']
                        cost = item['cost']
                        type_of = item['type_of']
                        sub_cat_id = item['sub_cat_id']
                        sub_cat_img = item['sub_cat_img']
                        section_type = item['section_type']
                        query_dry = "insert into vff.laundry_cart_items(catid,subcatid,customer_id,booking_id,booking_type,item_cost,item_quantity,type,cat_img,cat_name,sub_cat_name,sub_cat_img,actual_cost,section_type) values ('"+str(cat_id)+"','"+str(sub_cat_id)+"','"+str(customer_id)+"','"+str(booking_id)+"','"+str(booking_type)+"','"+str(cost)+"','"+str(item_quantity)+"','"+str(type_of)+"','"+str(cat_img)+"','"+str(cat_name)+"','"+str(sub_cat_name)+"','"+str(sub_cat_img)+"','"+str(actual_cost)+"','"+str(section_type)+"')"
                        cursor.execute(query_dry)
                        connection.commit();
            except Exception as e:
                print('---------Error Inserting Dry Clean Records--------')
                print(e)
                    
            

        #Load Cart Items
        cart_items_query = "select itemid,catid,subcatid,booking_id,dt,time,booking_type,item_cost,item_quantity,type,cat_img,cat_name,sub_cat_name,sub_cat_img,actual_cost,section_type from vff.laundry_cart_items where customer_id='"+str(customer_id)+"' and booking_id='"+str(booking_id)+"'"
        query_result = execute_raw_query(cart_items_query)
            
        cart_items_data = []    
        if not query_result == 500:
            for row in query_result:
                cart_items_data.append({
                    'itemid': row[0],
                    'catid': row[1],
                    'subcatid': row[2],
                    'booking_id': row[3],
                    'dt': row[4],
                    'time': row[5],
                    'booking_type': row[6],
                    'item_cost': row[7],
                    'item_quantity': row[8],
                    'type': row[9],
                    'cat_img': row[10],
                    'cat_name': row[11],
                    'sub_cat_name': row[12],
                    'sub_cat_img': row[13],
                    'actual_cost': row[14],
                    'section_type': row[15],
                })
        else:
            error_msg = 'Something Went Wrong'
        return JsonResponse({'cart_items_data':cart_items_data})
    
    
    return JsonResponse({'error_msg':error_msg})


#Delete Items in Cart
def delete_cart_item(request):
    
    isLogin = is_loggedin(request)
    if isLogin == False:
        return redirect('dashboard_app:login')
    
    
    msg = "Success"
    if request.method == "POST":
        jdict = json.loads(request.body)
        item_id=jdict['item_id']
        
        try:
            with connection.cursor() as cursor:
                delete_query = "delete from vff.laundry_cart_items where itemid='"+str(item_id)+"'"
                print(f'delete_query_items_cart Query::{delete_query}')
                cursor.execute(delete_query)
                connection.commit()
                
        except Exception as e:
            print(f"Error loading data: {e}")
            msg = f"Error:{e}"
    
    
    return JsonResponse({'msg':msg})


#ReLoad All Added Cart Items
def load_cart_items_after_deletion(request):
    #Load Cart Items
    jdict = json.loads(request.body)
    customer_id = jdict['customer_id']
    booking_id = jdict['booking_id']
    cart_items_query = "select itemid,catid,subcatid,booking_id,dt,time,booking_type,item_cost,item_quantity,type,cat_img,cat_name,sub_cat_name,sub_cat_img,actual_cost,section_type from vff.laundry_cart_items where customer_id='"+str(customer_id)+"' and booking_id='"+str(booking_id)+"'"
    query_result = execute_raw_query(cart_items_query)
        
    cart_items_data = []    
    if not query_result == 500:
        for row in query_result:
            cart_items_data.append({
                'itemid': row[0],
                'catid': row[1],
                'subcatid': row[2],
                'booking_id': row[3],
                'dt': row[4],
                'time': row[5],
                'booking_type': row[6],
                'item_cost': row[7],
                'item_quantity': row[8],
                'type': row[9],
                'cat_img': row[10],
                'cat_name': row[11],
                'sub_cat_name': row[12],
                'sub_cat_img': row[13],
                'actual_cost': row[14],
                'section_type': row[15],
            })
    else:
        error_msg = 'Something Went Wrong'
        return JsonResponse({'error':error_msg})
    return JsonResponse({'cart_items_data':cart_items_data})


#Load Delivered Sales CHart Details
def get_delivery_chart_details(request):
    #Load Cart Items
    branch_id = request.session.get('branchid')
    #query="select to_char(pickup_dt, 'YYYY-MM') AS month,COUNT(*) AS completed_order_count FROM vff.laundry_ordertbl WHERE order_completed = '1' AND branch_id = '"+str(branch_id)+"' GROUP BY month ORDER BY month;"
    query = "WITH MonthlyCounts AS (SELECT TO_DATE(to_char(pickup_dt, 'YYYY-MM') || '-01', 'YYYY-MM-DD') AS month, COUNT(*) AS completed_order_count FROM vff.laundry_ordertbl WHERE order_completed = '1' AND branch_id = '"+str(branch_id)+"' GROUP BY month) SELECT TO_CHAR(current_month.month, 'YYYY-MM') AS current_month, current_month.completed_order_count AS current_month_count, TO_CHAR(previous_month.month, 'YYYY-MM') AS previous_month, previous_month.completed_order_count AS previous_month_count, CASE WHEN previous_month.completed_order_count = 0 THEN 100 ELSE ((current_month.completed_order_count - previous_month.completed_order_count) / previous_month.completed_order_count) * 100 END AS percentage_increase FROM MonthlyCounts current_month LEFT JOIN MonthlyCounts previous_month ON current_month.month = previous_month.month + INTERVAL '1 month' ORDER BY current_month.month"
    query_result = execute_raw_query(query)
    
    data = []    
    
    if not query_result == 500:
        for row in query_result:
            data.append({
                'current_month': row[0],
                'current_month_count': row[1],
                'previous_month': row[2],
                'previous_month_count': row[3],
                'percentage_increase': row[4],
            })

    else:
        error_msg = 'Something Went Wrong'
        return JsonResponse({'error': error_msg})

    return JsonResponse({'data': data})

#Load  Sales CHart Details
def get_sales_chart_details(request):
    #Load Cart Items
    branch_id = request.session.get('branchid')
    
    query = "select to_char(pickup_dt, 'YYYY-MM') AS month,COUNT(*) AS completed_order_count FROM vff.laundry_ordertbl WHERE order_completed = '1' AND branch_id = '"+str(branch_id)+"' and order_taken_on='App'  GROUP BY month ORDER BY month"
    query_result = execute_raw_query(query)
    
    data = []    
    
    query2 = "select to_char(pickup_dt, 'YYYY-MM') AS month,COUNT(*) AS completed_order_count FROM vff.laundry_ordertbl WHERE order_completed = '1' AND branch_id = '"+str(branch_id)+"' and order_taken_on='OnCounter'  GROUP BY month ORDER BY month"
    query_result2 = execute_raw_query(query2)
    
    if not query_result == 500 and not query_result2 == 500:
        for row in query_result:
            data.append({
                'order_taken_on': 'App',
                'month': row[0],
                'completed_order_count': row[1],
            })

        for row in query_result2:
            data.append({
                'order_taken_on': 'OnCounter',
                'month': row[0],
                'completed_order_count': row[1],
            })
    else:
        error_msg = 'Something Went Wrong'
        return JsonResponse({'error': error_msg})

    return JsonResponse({'data': data})


#Load extra add ons items
def load_extra_items(request):
    #Load Cart Items
    jdict = json.loads(request.body)
    
    booking_id = jdict['booking_id']
    query="select extra_item_id,extra_item_name,price from vff.laundry_extra_items_tbl"
    query_result = execute_raw_query(query)
    
    extra_items_data = []    
    
    if not query_result == 500:
        for row in query_result:
            extra_items_data.append({
                'extra_item_id':row[0],
                'extra_item_name': row[1],
                'price' :row[2],
            })
                
    else:
        error_msg = 'Something Went Wrong'
        return JsonResponse({'error':error_msg})
    
    query2="select sum(item_cost) as total_price,sum(item_quantity) as total_quantity from vff.laundry_cart_items where booking_id='"+str(booking_id)+"'"
    query2_result = execute_raw_query(query2)
    
    sum_data = []
    if not query2_result == 500:
        for row in query2_result:
            sum_data.append({
                'total_cost':row[0],
                'total_quantity':row[1],
            })
    
    #To get delivery charges for delivery
    query3="select dcharge_id,price,range from vff.laundry_delivery_chargetbl"
    query3_result = execute_raw_query(query3)
    
    delivery_charges_data = []
    if not query3_result == 500:
        for row in query3_result:
            delivery_charges_data.append({
                'dcharge_id':row[0],
                'delivery_price':row[1],
                'delivery_range':row[2],
            })
    
    
    return JsonResponse({'extra_items_data':extra_items_data,'sum_data':sum_data,'delivery_charges_data':delivery_charges_data})


#Generate Booking ID
def generate_booking_id(request):
    
    isLogin = is_loggedin(request)
    if isLogin == False:
        return redirect('dashboard_app:login')
    
    
    error_msg = "Something Went Wrong"
    if request.method == "POST":
        jdict = json.loads(request.body)
        customer_id = jdict['customer_id']
        
        booking_status = "Accepted"
        print(f'customer_id_given:::{customer_id}')
        fetch_customer_records = "select address,city,pincode,landmark,branchid from  vff.usertbl,vff.laundry_customertbl where laundry_customertbl.usrid=usertbl.usrid and consmrid='"+str(customer_id)+"'"
        try:
            with connection.cursor() as cursor:    
                cursor.execute(fetch_customer_records)
                row = cursor.fetchone()
                print(f'fetch_customer_records_query::{row}')
                if row:
                    streetAddress= row[0]
                    cityName = row[1]
                    zipCode = row[2]
                    landMark = row[3]
                    branch_id = row[4]
                        
                        
        except Exception as e:
                print(f"Error loading data: {e}")
                
        
        
            
        try:
            with connection.cursor() as cursor:
                create_new_booking = "insert into vff.laundry_order_bookingtbl(customerid,address,city,pincode,landmark,branch_id,booking_status,booking_taken_on) values ('"+str(customer_id)+"','"+str(streetAddress)+"','"+str(cityName)+"','"+str(zipCode)+"','"+str(landMark)+"','"+str(branch_id)+"','"+str(booking_status)+"','OnCounterBooking') returning bookingid" 
                cursor.execute(create_new_booking)
                booking_id = cursor.fetchone()[0]
                print(f'Retuning BOOKING ID-------->{booking_id}')
                connection.commit()
                
        except Exception as e:
            print(f"Error loading data: {e}")
            #order_accept_tbl = "insert into vff.laundry_delivery_accept_tbl(delivery_boy_id,status,booking_id,branch_id) values ('"+str(delivery_boy_id)+"','"+str(status)+"','"+str(booking_id)+"','"+str(branch_id)+"')"
            ##Order Assignment
            #query5="insert into vff.laundry_order_assignmenttbl(booking_id,delivery_boy_id,type_of_order) values ('"+str(booking_id)+"','"+str(delivery_boy_id)+"','Pickup')"//"Accepted"
        return JsonResponse({'booking_id':booking_id})
            

    
    
    return JsonResponse({'error_msg':error_msg})





#Place Order
def place_new_order(request):
    
    isLogin = is_loggedin(request)
    if isLogin == False:
        return redirect('dashboard_app:login')
    
    
    error_msg = "Something Went Wrong"
    if request.method == "POST":
        jdict = json.loads(request.body)
        booking_id = jdict['booking_id']
        delivery_price = jdict['delivery_price']
        discount_price = jdict['discount_price']
        gstamount = jdict['gstamount']
        igstamount = jdict['igstamount']
        customer_id = jdict['customer_id']
        total_price = jdict['total_price']
        total_items = jdict['total_items']
        order_status = "Payment Done"
        razor_pay_id = jdict['razor_pay_id']
        payment_status = jdict['payment_status']
        payment_type = jdict['payment_type']
        extra_item_dict = jdict['extra_items']
        additional_instruction = jdict['additional_instruction']
        dateofdelivery = jdict['dateofdelivery']
        wantsDelivery = jdict['wantsDelivery']

        branch_id = request.session.get('branchid')
        print(f'total_price::{total_price}')
        try:
            with connection.cursor() as cursor:
                #Insert Record into Order Table First to Generate Order ID
                #Adding delivery_boyid = 1 for counter orders only
                query_order = "insert into vff.laundry_ordertbl(customerid,quantity,price,order_status,additional_instruction,booking_id,delivery_price,discount_price,delivery,delivery_boyid,gstamount,igstamount,branch_id,order_taken_on,wants_delivery) values ('"+str(customer_id)+"','"+str(total_items)+"','"+str(total_price)+"','"+str(order_status)+"','"+str(additional_instruction)+"','"+str(booking_id)+"','"+str(delivery_price)+"','"+str(discount_price)+"','"+str(dateofdelivery)+"','1','"+str(gstamount)+"','"+str(igstamount)+"','"+str(branch_id)+"','OnCounter','"+str(wantsDelivery)+"') returning orderid"
                cursor.execute(query_order)
                order_id = cursor.fetchone()[0]
                print(f'Retuning BOOKING ID-------->{order_id}')
                connection.commit()
                
                #Insert record in payment table with razorpay_payment_id
                query_payment = "insert into vff.laundry_payment_tbl(order_id,razor_pay_payment_id,status,payment_type,branch_id) values ('"+str(order_id)+"','"+str(razor_pay_id)+"','"+str(payment_status)+"','"+str(payment_type)+"','"+str(branch_id)+"')"
                print(f'insert payment::{query_payment}')
                cursor.execute(query_payment)
                connection.commit()
                
                #Adding all cart items into active order table 
                query_active_orders="insert into vff.laundry_active_orders_tbl(order_id,booking_id,categoryid,subcategoryid,booking_type,item_cost,item_quantity,type,cat_img,cat_name,sub_cat_name,sub_cat_img,actual_cost,section_type) select "+str(order_id)+" as order_id,booking_id,catid,subcatid,booking_type,item_cost,item_quantity,type,cat_img,cat_name,sub_cat_name,sub_cat_img,actual_cost,section_type from vff.laundry_cart_items where customer_id='"+str(customer_id)+"' and booking_id='"+str(booking_id)+"'"
                print(f'query_active_orders::{query_active_orders}')
                cursor.execute(query_active_orders)
                connection.commit()
                
                #insert extra items selected by customer while checking out
                print(f'extra_item_dict::{extra_item_dict}')
                try:
                    for item in extra_item_dict:
                        print('--------------------Trying to add----------------')
                        extra_id = item['extra_item_id']
                        print(f'extra_item_id:::{extra_id}')
                        extra_item_price = item['extra_item_price']
                        extra_name = item['extra_item_name']
                        query3="insert into vff.laundry_cart_extra_items_tbl(extra_item_id,price,extra_item_name,order_id) values ('"+str(extra_id)+"','"+str(extra_item_price)+"','"+str(extra_name)+"','"+str(order_id)+"')"
                        print(f"Qeury3:::{query3}")
                        cursor.execute(query3)
                        connection.commit()
                  #  obj.reply_data="ErrorCode#0"
                except Exception as e:
                    print(e)
                    
                #Update Order status
                update_order_status_while_placing_order(request,order_id,order_status)
                    

                
        except Exception as e:
            print(f"Error Placing New Order: {e}")
            error_msg = 'Something went wrong'
            return JsonResponse({'error':error_msg})
        
            

    
    return JsonResponse({'html':'html'})
    #return redirect('dashboard_app:all_orders')

def update_order_status_while_placing_order(request,order_id,status):
    try:
        with connection.cursor() as cursor:
            query="insert into vff.laundry_order_historytbl(order_id,order_stages) values ('"+str(order_id)+"','"+str(status)+"')"
            cursor.execute(query)
            connection.commit()
            print(f'Order status updated to {status} for order ID::{order_id}')
    except Exception as e:
            print(f"Error Updating Order Status: {e}")
    
#All Expenses
def all_expenses(request):
    isLogin = is_loggedin(request)
    if isLogin == False:
        return redirect('dashboard_app:login')
    error_msg = "No Expenses Record Found"
    branch_id = request.session.get('branchid')
    
    query_all_categories = "select expcatid,category_name,category_type,status from vff.laundry_expense_categorytbl"
    result_categories = execute_raw_query(query_all_categories)
    
    data_category = []    
    if not result_categories == 500:
        for row in result_categories:
            
            data_category.append({
                'expcatid': row[0],
                'category_name': row[1],
                'category_type': row[2],
                'status': row[3],  
            })
    
    filter = ''
    if branch_id :
        filter = " where branch_id='"+str(branch_id)+"'"
        
    #query = "select expensesid,exp_catgry_name,exp_catid,exp_amount,payment_mode,tax_included,tax_percentage,extra_note,epoch_time,date from vff.laundry_expensestbl  where branch_id='"+str(branch_id)+"' and date>='"+str(start_date)+"' and date<='"+str(end_date)+"' order by expensesid desc"
    query = "select expensesid,exp_catgry_name,exp_catid,exp_amount,payment_mode,tax_included,tax_percentage,extra_note,epoch_time,date from vff.laundry_expensestbl  where branch_id='"+str(branch_id)+"'  order by expensesid desc"
    query_result = execute_raw_query(query)
    
    
        
    data = []    
    if not query_result == 500:
        for row in query_result:
            
            data.append({
                'expensesid': row[0],
                'exp_catgry_name': row[1],
                'exp_catid': row[2],
                'exp_amount': row[3],
                'payment_mode': row[4],
                'tax_included': row[5],
                'tax_percentage': row[6],
                'extra_note': row[7],
                'epoch_time': row[8],
                'date': row[9],
               
            })
    else:
        error_msg = 'Something Went Wrong'
    current_url = request.get_full_path()
    # using the 'current_url' variable to determine the active card.
    context = {'query_result': data,'data_all_categories':data_category,'current_url': current_url,'error_msg':error_msg}
    
    return render(request, 'expenses_pages/all_expenses_list.html', context)

#Expenses Category
def expense_category(request):
    isLogin = is_loggedin(request)
    if isLogin == False:
        return redirect('dashboard_app:login')
    error_msg = "No Expense Category added till now"
    branch_id = request.session.get('branchid')
    filter = ''
    
    query = "select expcatid,category_name,category_type,status from vff.laundry_expense_categorytbl order by expcatid"
    
    query_result = execute_raw_query(query)
    
    
        
    data = []    
    if not query_result == 500:
        for row in query_result:
            
            data.append({
                'expcatid': row[0],
                'category_name': row[1],
                'category_type': row[2],
                'status': row[3],
                
               
            })
    else:
        error_msg = 'Something Went Wrong'
    current_url = request.get_full_path()
    # using the 'current_url' variable to determine the active card.
    context = {'query_result': data,'current_url': current_url,'error_msg':error_msg}
    
    return render(request, 'expenses_pages/expense_categories.html', context)

#Add Expense Category
def add_expense_category(request):
    isLogin = is_loggedin(request)
    if isLogin == False:
        return redirect('dashboard_app:login')
    error_msg = ""
    branch_id = request.session.get('branchid')
    if request.method == "POST":
        category_name = request.POST.get('category_name')
        category_type = request.POST.get('category_type')
        try:
            with connection.cursor() as cursor:
                
                insert_query = "insert into vff.laundry_expense_categorytbl(category_name,category_type) values ('"+str(category_name)+"','"+str(category_type)+"') "
                cursor.execute(insert_query)

                connection.commit()

                print("Expense category Added/Updated Successfully.")
                return redirect('dashboard_app:expense_category')
        except Exception as e:
            print(f"Error loading data: {e}")
    current_url = request.get_full_path()
    # using the 'current_url' variable to determine the active card.
    # context = {'query_result': data,'current_url': current_url,'error_msg':error_msg}
    
    return render(request, 'expenses_pages/expense_categories.html', {'current_url': current_url})

#Add Expense New Item
def add_expense_new_item(request):
    isLogin = is_loggedin(request)
    if isLogin == False:
        return redirect('dashboard_app:login')
    error_msg = ""
    branch_id = request.session.get('branchid')
    if not branch_id:
        branch_id = 1
    if request.method == "POST":
        dateofexpense = request.POST.get('dateofexpense')
        exp_category = request.POST.get('exp_category')
        exp_amount = request.POST.get('exp_amount')
        invoice_no = request.POST.get('invoice_no')
        company_name = request.POST.get('company_name')
        payment_mode = request.POST.get('payment_mode')
        tax_included = request.POST.get("taxIncluded")
        tax_percentage = request.POST.get("taxPercentage")
        notes = request.POST.get("notes")
        exp_catid = request.POST.get('selectedCategoryId')
        print(f'exp_catid:::{exp_catid}')
        tax = 0
        if not company_name:
            company_name = 'NA'
        if not invoice_no:
            invoice_no = 'NA'
        if not notes:
            notes='NA'
        if not tax_percentage:
            tax_percentage = 0
        if tax_included == "yes":
            # The tax is included, and you can access the tax percentage
            print("Tax is included, and the percentage is:", tax_percentage)
            tax = 1
        else:
            # Tax is not included
            print("Tax is not included")
        try:
            with connection.cursor() as cursor:
                
                insert_query = "insert into vff.laundry_expensestbl (exp_catgry_name,exp_catid,exp_amount,payment_mode,tax_included,tax_percentage,extra_note,date,branch_id,invoice_no,company_name) values ('"+str(exp_category)+"','"+str(exp_catid)+"','"+str(exp_amount)+"','"+str(payment_mode)+"','"+str(tax)+"','"+str(tax_percentage)+"','"+str(notes)+"','"+str(dateofexpense)+"','"+str(branch_id)+"','"+str(invoice_no)+"','"+str(company_name)+"')"
                cursor.execute(insert_query)

                connection.commit()

                print(f"New Expenses Item {exp_category} Added Successfully.")
                return redirect('dashboard_app:all_expenses')
        except Exception as e:
            print(f"Error loading data: {e}")
    return redirect('dashboard_app:all_expenses')



#Orders Status Screen
def order_status_screen(request):
    isLogin = is_loggedin(request)
    if isLogin == False:
        return redirect('dashboard_app:login')
    error_msg = "No Categories Found"
    branch_id = request.session.get('branchid')
    # filter = ''
    # if branch_id :
    #     filter = " and laundry_delivery_boytbl.branchid='"+str(branch_id)+"'"
    # query = "select catid,category_name,cat_img,regular_price,regular_price_type,express_price,express_price_type,offer_price,offer_price_type,description from vff.laundry_categorytbl order by catid desc"
    
    # query_result = execute_raw_query(query)
    
    
        
    # data = []    
    # if not query_result == 500:
    #     for row in query_result:
            
    #         data.append({
    #             'catid': row[0],
    #             'categoryname': row[1],
    #             'categoryimg': row[2],
    #             'regular_prize': row[3],
    #             'regular_prize_type': row[4],
    #             'express_prize': row[5],
    #             'express_prize_type': row[6],
    #             'offer_prize': row[7],
    #             'offer_prize_type': row[8],
    #             'description': row[9],
               
    #         })
    # else:
    #     error_msg = 'Something Went Wrong'
    current_url = request.get_full_path()
    # using the 'current_url' variable to determine the active card.
    # context = {'query_result': data,'current_url': current_url,'error_msg':error_msg}
    
    return render(request, 'order_pages/orders_status_screen.html', {'current_url': current_url})

#Counter Orders Assign
def counter_orders_screen(request):
    isLogin = is_loggedin(request)
    if isLogin == False:
        return redirect('dashboard_app:login')
    error_msg = "No Categories Found"
    branch_id = request.session.get('branchid')
    filter = ''
   #CategoryWise Details
   #select category_name,regular_price,regular_price_type,express_price_type,express_price,offer_price,offer_price_type,cat_img from vff.laundry_categorytbl where catid='"+str(cat_id)+"'
   
   #Sub Categorywise Details
   #select sub_cat_name,sub_cat_img,cost,type,section_type,subcatid from vff.laundry_sub_categorytbl where catid='"+str(cat_id)+"'
   
    query = "select catid,category_name,cat_img,regular_price,regular_price_type,express_price,express_price_type,offer_price,offer_price_type,description,min_hours from vff.laundry_categorytbl order by category_name "
    
    query_result = execute_raw_query(query)
    
    
        
    category_data = []    
    if not query_result == 500:
        for row in query_result:
            
            category_data.append({
                'catid': row[0],
                'categoryname': row[1],
                'cat_img': row[2],
                'regular_prize': row[3],
                'regular_prize_type': row[4],
                'express_prize': row[5],
                'express_prize_type': row[6],
                'offer_prize': row[7],
                'offer_prize_type': row[8],
                'description': row[9],
                'min_hours': row[9],
               
            })
    else:
        error_msg = 'Something Went Wrong'
    current_url = request.get_full_path()
    # using the 'current_url' variable to determine the active card.
    context = {'category_data': category_data,'current_url': current_url,'error_msg':error_msg}
    
    return render(request, 'order_pages/counter_orders_assign_page.html', context)

def load_other_category_wise_details(request,cat_id):
    print(f'other service cat_id ::{cat_id}')
    try:
        other_category_data = [] 
        with connection.cursor() as cursor:
                query = "select category_name,regular_price,regular_price_type,express_price_type,express_price,offer_price,offer_price_type,cat_img from vff.laundry_categorytbl where catid='"+str(cat_id)+"'"
                cursor.execute(query)
                row = cursor.fetchone()
                print(f'response_query::{row}')
                if row:
                    other_category_data = {
                        'category_name': row[0],
                'regular_price': row[1],
                'regular_price_type': row[2],
                'express_price_type': row[3],
                'express_price': row[4],
                'offer_price': row[5],
                'offer_price_type': row[6],
                'cat_img':row[7],
                'catid':cat_id,
                    }
    except Exception as e:
            print(f"Error loading data: {e}")
    
    
    context = {'other_category_data':other_category_data}
    return JsonResponse(context)
    
def load_sub_categories(request,cat_id):
    query = "select sub_cat_name,sub_cat_img,cost,type,section_type,subcatid from vff.laundry_sub_categorytbl where catid='"+str(cat_id)+"' order by sub_cat_name"
    
    query_result = execute_raw_query(query)
    
    query2 = "select sectionid,section_name from vff.laundry_sub_category_sectiontbl order by section_name"
    query2_result = execute_raw_query(query2)
    
    section_data = []
    if not query2_result == 500:
        for row in query2_result:
            section_data.append({
                'sectionid':row[0],
                'section_name':row[1]
            })
        
    sub_category_data = []    
    if not query_result == 500:
        for row in query_result:
            
            sub_category_data.append({
                'sub_cat_name': row[0],
                'sub_cat_img': row[1],
                'cost': row[2],
                'type': row[3],
                'section_type': row[4],
                'subcatid': row[5],
            })
    else:
        error_msg = 'Something Went Wrong'
        return JsonResponse({'error_msg':error_msg});
        
    context = {'sub_categories':sub_category_data,'section_data':section_data}
    return JsonResponse(context)
    
def load_section_type_sub_categories(request,section_type):
    query = "select sub_cat_name,sub_cat_img,cost,type,subcatid from vff.laundry_sub_categorytbl where section_type='"+str(section_type)+"' order by sub_cat_name"
    
    query_result = execute_raw_query(query)
    
    
        
    sub_category_data = []    
    if not query_result == 500:
        for row in query_result:
            
            sub_category_data.append({
                'sub_cat_name': row[0],
                'sub_cat_img': row[1],
                'cost': row[2],
                'type': row[3],
                'subcatid': row[4],
                
            })
    else:
        error_msg = 'Something Went Wrong'
        return JsonResponse({'error_msg':error_msg});
        
    context = {'sub_categories':sub_category_data}
    return JsonResponse(context)


#Daily Reports Screen
def daily_report(request):
    isLogin = is_loggedin(request)
    if isLogin == False:
        return redirect('dashboard_app:login')
    error_msg = "No Categories Found"
    branch_id = request.session.get('branchid')
    totalOrder = 0
    totalEarnings = 0
    totalExpense = 0
    totalOrderDelievered = 0
    today_date = datetime.now().strftime("%Y-%m-%d")
    print(today_date)
    todayDT = today_date
    #Total Orders 
    query_total_orders = "select count(*) from vff.laundry_ordertbl where pickup_dt='"+str(today_date)+"'  and branch_id='"+str(branch_id)+"'";
    query_total_orders_result = execute_raw_query_fetch_one(query_total_orders)
    print(f'query_total_orders_result:{query_total_orders_result}')
    if query_total_orders_result:   
        totalOrder = query_total_orders_result[0]
        
    #No of Orders Delivered
    query_total_orders_delievered = "select count(*) from vff.laundry_ordertbl where pickup_dt='"+str(today_date)+"' and order_completed='1' and branch_id='"+str(branch_id)+"'";
    query_total_orders_delievered_result = execute_raw_query_fetch_one(query_total_orders_delievered)
    if query_total_orders_delievered_result:   
        totalOrderDelievered = query_total_orders_delievered_result[0]
    
    #Total Earnings Today
    earning_total = "select sum(price) from vff.laundry_ordertbl where pickup_dt='"+str(today_date)+"' and branch_id='"+str(branch_id)+"'";
    earning_total_result = execute_raw_query_fetch_one(earning_total)
    if earning_total_result != None:   
        if earning_total_result[0] != None:
            totalEarnings = earning_total_result[0]
    
    #Total Expenses Today
    #select sum(exp_amount) from vff.laundry_expensestbl where date='2023-10-31' and branch_id='1';
    expense_total = "select sum(exp_amount) from vff.laundry_expensestbl where date='"+str(today_date)+"' and branch_id='"+str(branch_id)+"'"
    expense_total_result = execute_raw_query_fetch_one(expense_total)
    if expense_total_result != None:   
        if expense_total_result[0] != None:
            totalExpense = expense_total_result[0]
    
    
    current_url = request.get_full_path()
    # using the 'current_url' variable to determine the active card.
    context = {'todayDT':today_date,'totalOrder': totalOrder,'totalOrderDelievered': totalOrderDelievered,'totalEarnings': totalEarnings,'totalExpense': totalExpense,'current_url': current_url,'error_msg':error_msg}
    
    return render(request, 'reports/daily_report.html', context)

def search_customer_to_assign_order(request,mobno):
    
    # mobno = request.GET.get('mobno', '')
    print(f'Mobile No::{mobno}')
    query = "select consmrid,customer_name,company_name,gstno,igstno,mobile_no from vff.usertbl,vff.laundry_customertbl where laundry_customertbl.usrid=usertbl.usrid and mobile_no ILIKE '"+str(mobno)+"%'"
    query_result = execute_raw_query(query)
               
    

    data = []
    if query_result == 500:
        return redirect('dashboard_app:counter_orders_screen')
    elif query_result:
        for row in query_result:
            data.append({
                'consmrid': row[0],
                'customer_name': row[1],
                'company_name': row[2],
                'gstno': row[3],
                'igstno': row[4],
                'mobile_no': row[5],
            })
    current_url = request.get_full_path()
    
    context = {'suggestions': data,'current_url': current_url}
    return JsonResponse(context)
    # return render(request, 'order_pages/counter_orders_assign_page.html', context)
    
#Orders Reports Screen
def order_report(request):
    isLogin = is_loggedin(request)
    if isLogin == False:
        return redirect('dashboard_app:login')
    error_msg = ""
    branch_id = request.session.get('branchid')
    if request.method=="POST":
        jdict = json.loads(request.body)
        start_date = jdict['start_date']
        end_date = jdict['end_date']
        order_type = jdict['order_type']
        filter = ''
        if order_type == "All Orders":
            filter = "order_status !='NA' "
        else:
            filter = "order_status ='"+str(order_type)+"' "
        query = "select consmrid,usertbl.usrid,customer_name,mobile_no,houseno,address,city,pincode,landmark,profile_img,device_token,orderid,delivery_boyid,quantity,price,pickup_dt,delivery,clat,clng,order_completed,order_status,additional_instruction,laundry_ordertbl.epoch,cancel_reason,feedback,delivery_epoch,name as deliveryboy_name from vff.laundry_ordertbl,vff.laundry_customertbl,vff.usertbl,vff.laundry_delivery_boytbl where laundry_customertbl.usrid=usertbl.usrid and laundry_ordertbl.customerid=laundry_customertbl.consmrid and laundry_ordertbl.delivery_boyid=laundry_delivery_boytbl.delivery_boy_id and "+filter+" and pickup_dt>='"+str(start_date)+"' and pickup_dt<='"+str(end_date)+"' and branch_id='"+str(branch_id)+"'  order by orderid desc"

        query_result = execute_raw_query(query)



        data = []    
        if not query_result == 500:
            for row in query_result:
                depoch = row[25]#delivery epoch
                oepoch = row[22]#order taken epoch
                orderStatus = row[20]
                deliveryEpoch = epochToDateTime(depoch)
                orderTakenEpoch = epochToDateTime(oepoch)
                if orderStatus != "Completed":
                    deliveryEpoch = "Not Delivered Yet"

                data.append({
                    'consmrid': row[0],
                    'usrid': row[1],
                    'customer_name': row[2],
                    'mobile_no': row[3],
                    'houseno': row[4],
                    'address': row[5],
                    'city': row[6],
                    'pincode': row[7],
                    'landmark': row[8],
                    'profile_img': row[9],
                    'device_token': row[10],
                    'orderid': row[11],
                    'delivery_boyid': row[12],
                    'quantity':row[13],
                    'price': row[14],
                    'pickup_dt': row[15],
                    'delivery_dt': row[16],
                    'clat': row[17],
                    'clng': row[18],
                    'order_completed': row[19],
                    'order_status': orderStatus,
                    'additional_instruction': row[21],
                    'order_taken_epoch': orderTakenEpoch,
                    'cancel_reason': row[23],
                    'feedback': row[24],
                    'delivery_epoch': deliveryEpoch,
                    'delivery_boy_name': row[26],



                })
            
        else:
            error_msg = 'Something Went Wrong'
            
        return JsonResponse({'data':data})
    
    current_url = request.get_full_path()
    # using the 'current_url' variable to determine the active card.
    # context = {'query_result': data,'current_url': current_url,'error_msg':error_msg}
    
    return render(request, 'reports/orders_report.html', {'current_url': current_url})

#Sales Reports Screen
def sales_report(request):
    isLogin = is_loggedin(request)
    if isLogin == False:
        return redirect('dashboard_app:login')
    error_msg = ""
    branch_id = request.session.get('branchid')
    #select consmrid,usertbl.usrid,customer_name,mobile_no,houseno,address,city,pincode,landmark,profile_img,device_token,orderid,delivery_boyid,quantity,laundry_ordertbl.price,pickup_dt,delivery,clat,clng,order_completed,order_status,additional_instruction,laundry_ordertbl.epoch,cancel_reason,feedback,delivery_epoch,name as deliveryboy_name,gstamount,igstamount,discount_price,delivery_price,sum(laundry_cart_extra_items_tbl.price) as addons_price from vff.laundry_ordertbl,vff.laundry_customertbl,vff.usertbl,vff.laundry_delivery_boytbl,vff.laundry_cart_extra_items_tbl where laundry_customertbl.usrid=usertbl.usrid and laundry_ordertbl.customerid=laundry_customertbl.consmrid and laundry_ordertbl.delivery_boyid=laundry_delivery_boytbl.delivery_boy_id and laundry_cart_extra_items_tbl.order_id=laundry_ordertbl.orderid and order_status ='Payment Done'  and pickup_dt>='2023-11-01' and pickup_dt<='2023-11-11' and branch_id='1' GROUP BY consmrid,usertbl.usrid,customer_name,mobile_no,houseno,address,city,pincode,landmark,profile_img,device_token,orderid,delivery_boyid,quantity,laundry_ordertbl.price,pickup_dt,delivery,clat,clng,order_completed,order_status,additional_instruction,laundry_ordertbl.epoch,cancel_reason,feedback,delivery_epoch,name,gstamount,igstamount,discount_price,delivery_price order by orderid desc
    #select consmrid,usertbl.usrid,customer_name,mobile_no,houseno,address,city,pincode,landmark,profile_img,device_token,orderid,delivery_boyid,quantity,laundry_ordertbl.price,pickup_dt,delivery,clat,clng,order_completed,order_status,additional_instruction,laundry_ordertbl.epoch,cancel_reason,feedback,delivery_epoch,name as deliveryboy_name,gstamount,igstamount,discount_price,delivery_price,sum(laundry_cart_extra_items_tbl.price) as addons_price,item_cost from vff.laundry_active_orders_tbl,vff.laundry_ordertbl,vff.laundry_customertbl,vff.usertbl,vff.laundry_delivery_boytbl,vff.laundry_cart_extra_items_tbl where laundry_customertbl.usrid=usertbl.usrid and laundry_ordertbl.customerid=laundry_customertbl.consmrid and laundry_ordertbl.delivery_boyid=laundry_delivery_boytbl.delivery_boy_id and laundry_active_orders_tbl.order_id=laundry_ordertbl.orderid and  laundry_ordertbl.delivery_boyid=laundry_delivery_boytbl.delivery_boy_id and laundry_cart_extra_items_tbl.order_id=laundry_ordertbl.orderid and order_status ='Payment Done'  and pickup_dt>='2023-11-01' and pickup_dt<='2023-11-11' and branch_id='1' GROUP BY consmrid,usertbl.usrid,customer_name,mobile_no,houseno,address,city,pincode,landmark,profile_img,device_token,orderid,delivery_boyid,quantity,laundry_ordertbl.price,pickup_dt,delivery,clat,clng,order_completed,order_status,additional_instruction,laundry_ordertbl.epoch,cancel_reason,feedback,delivery_epoch,name,gstamount,igstamount,discount_price,delivery_price,item_cost order by orderid desc
    if request.method=="POST":
        jdict = json.loads(request.body)
        start_date = jdict['start_date']
        end_date = jdict['end_date']
        
        filter = ''
        
        query = "select consmrid,usertbl.usrid,customer_name,mobile_no,houseno,address,city,pincode,landmark,profile_img,device_token,orderid,delivery_boyid,quantity,laundry_ordertbl.price,pickup_dt,delivery,clat,clng,order_completed,order_status,additional_instruction,laundry_ordertbl.epoch,cancel_reason,feedback,delivery_epoch,name as deliveryboy_name,gstamount,igstamount,discount_price,delivery_price,sum(laundry_cart_extra_items_tbl.price) as addons_price from vff.laundry_ordertbl,vff.laundry_customertbl,vff.usertbl,vff.laundry_delivery_boytbl,vff.laundry_cart_extra_items_tbl where laundry_customertbl.usrid=usertbl.usrid and laundry_ordertbl.customerid=laundry_customertbl.consmrid and laundry_ordertbl.delivery_boyid=laundry_delivery_boytbl.delivery_boy_id and order_status!='NA'  and pickup_dt>='"+str(start_date)+"' and pickup_dt<='"+str(end_date)+"' and branch_id='"+str(branch_id)+"' GROUP BY consmrid,usertbl.usrid,customer_name,mobile_no,houseno,address,city,pincode,landmark,profile_img,device_token,orderid,delivery_boyid,quantity,laundry_ordertbl.price,pickup_dt,delivery,clat,clng,order_completed,order_status,additional_instruction,laundry_ordertbl.epoch,cancel_reason,feedback,delivery_epoch,name,gstamount,igstamount,discount_price,delivery_price order by orderid desc"

        query_result = execute_raw_query(query)



        data = []    
        if not query_result == 500:
            for row in query_result:
                depoch = row[25]#delivery epoch
                oepoch = row[22]#order taken epoch
                orderStatus = row[20]
                deliveryEpoch = epochToDateTime(depoch)
                orderTakenEpoch = epochToDateTime(oepoch)
                if orderStatus != "Completed":
                    deliveryEpoch = "Not Delivered Yet"

                data.append({
                    'consmrid': row[0],
                    'usrid': row[1],
                    'customer_name': row[2],
                    'mobile_no': row[3],
                    'houseno': row[4],
                    'address': row[5],
                    'city': row[6],
                    'pincode': row[7],
                    'landmark': row[8],
                    'profile_img': row[9],
                    'device_token': row[10],
                    'orderid': row[11],
                    'delivery_boyid': row[12],
                    'quantity':row[13],
                    'price': row[14],
                    'pickup_dt': row[15],
                    'delivery_dt': row[16],
                    'clat': row[17],
                    'clng': row[18],
                    'order_completed': row[19],
                    'order_status': orderStatus,
                    'additional_instruction': row[21],
                    'order_taken_epoch': orderTakenEpoch,
                    'cancel_reason': row[23],
                    'feedback': row[24],
                    'delivery_epoch': deliveryEpoch,
                    'delivery_boy_name': row[26],
                    'gstamount': row[27],
                    'igstamount': row[28],
                    'discount_price': row[29],
                    'delivery_price': row[30],
                    'addons_price': row[31],



                })
            
        else:
            error_msg = 'Something Went Wrong'
            
        return JsonResponse({'data':data})
    
    
    current_url = request.get_full_path()
    # using the 'current_url' variable to determine the active card.
    # context = {'query_result': data,'current_url': current_url,'error_msg':error_msg}
    
    return render(request, 'reports/sales_report.html', {'current_url': current_url})

#Expense Reports Screen
def expense_report(request):
    isLogin = is_loggedin(request)
    if isLogin == False:
        return redirect('dashboard_app:login')
    error_msg = ""
    branch_id = request.session.get('branchid')
    # filter = ''
    # if branch_id :
    #     filter = " and laundry_delivery_boytbl.branchid='"+str(branch_id)+"'"
    # query = "select catid,category_name,cat_img,regular_price,regular_price_type,express_price,express_price_type,offer_price,offer_price_type,description from vff.laundry_categorytbl order by catid desc"
    
    # query_result = execute_raw_query(query)
    
    
        
    # data = []    
    # if not query_result == 500:
    #     for row in query_result:
            
    #         data.append({
    #             'catid': row[0],
    #             'categoryname': row[1],
    #             'categoryimg': row[2],
    #             'regular_prize': row[3],
    #             'regular_prize_type': row[4],
    #             'express_prize': row[5],
    #             'express_prize_type': row[6],
    #             'offer_prize': row[7],
    #             'offer_prize_type': row[8],
    #             'description': row[9],
               
    #         })
    # else:
    #     error_msg = 'Something Went Wrong'
    current_url = request.get_full_path()
    # using the 'current_url' variable to determine the active card.
    # context = {'query_result': data,'current_url': current_url,'error_msg':error_msg}
    
    return render(request, 'reports/expense_report.html', {'current_url': current_url})

#Tax Reports Screen
def tax_report(request):
    isLogin = is_loggedin(request)
    if isLogin == False:
        return redirect('dashboard_app:login')
    error_msg = ""
    branch_id = request.session.get('branchid')
    # filter = ''
    # if branch_id :
    #     filter = " and laundry_delivery_boytbl.branchid='"+str(branch_id)+"'"
    # query = "select catid,category_name,cat_img,regular_price,regular_price_type,express_price,express_price_type,offer_price,offer_price_type,description from vff.laundry_categorytbl order by catid desc"
    
    # query_result = execute_raw_query(query)
    
    
        
    # data = []    
    # if not query_result == 500:
    #     for row in query_result:
            
    #         data.append({
    #             'catid': row[0],
    #             'categoryname': row[1],
    #             'categoryimg': row[2],
    #             'regular_prize': row[3],
    #             'regular_prize_type': row[4],
    #             'express_prize': row[5],
    #             'express_prize_type': row[6],
    #             'offer_prize': row[7],
    #             'offer_prize_type': row[8],
    #             'description': row[9],
               
    #         })
    # else:
    #     error_msg = 'Something Went Wrong'
    current_url = request.get_full_path()
    # using the 'current_url' variable to determine the active card.
    # context = {'query_result': data,'current_url': current_url,'error_msg':error_msg}
    
    return render(request, 'reports/tax_report.html', {'current_url': current_url})


#Payment Receipt Screen
def payment_receipt(request):
    isLogin = is_loggedin(request)
    if isLogin == False:
        return redirect('dashboard_app:login')
    error_msg = ""
    
    current_url = request.get_full_path()
    # using the 'current_url' variable to determine the active card.
    # context = {'query_result': data,'current_url': current_url,'error_msg':error_msg}
    
    return render(request, 'payment_pages/payment_receipts.html', {'current_url': current_url})

#Payment Receipt Screen
def load_payment_receipt(request, start_date, end_date):
    isLogin = is_loggedin(request)
    if isLogin == False:
        return redirect('dashboard_app:login')
    error_msg = ""
    branch_id = request.session.get('branchid')
    filter = ''
    if branch_id :
        filter = " and  laundry_ordertbl.branch_id='"+str(branch_id)+"'"
    query = "select laundry_receipt_invoice_tbl.date,orderid,customer_name,price,payment_type,additional_instruction,payment_id,gstamount,igstamount,razor_pay_payment_id from vff.laundry_ordertbl,vff.laundry_receipt_invoice_tbl,vff.laundry_customertbl,vff.laundry_payment_tbl where laundry_ordertbl.orderid=laundry_receipt_invoice_tbl.order_id and laundry_ordertbl.orderid=laundry_payment_tbl.order_id and laundry_ordertbl.customerid=laundry_customertbl.consmrid and laundry_ordertbl.pickup_dt>='"+str(start_date)+"' and laundry_ordertbl.pickup_dt<='"+str(end_date)+"' "+filter+" order by orderid desc"
    
    query_result = execute_raw_query(query)
    
    
        
    data = []    
    total_amount = 0
    total_gst = 0
    total_igst = 0
    total_tax = 0
    if not query_result == 500:
        for row in query_result:
            total_tax 
            total_amount += float(row[3])
            gst = float(row[7])
            
            total_gst += gst
            
            igst = float(row[8])
            
            total_igst += igst
            
            total_tax += (gst + igst)
            
            
            data.append({
                'date': row[0],
                'order_id': row[1],
                'customer': row[2],
                'amount': row[3],
                'payment_type': row[4],
                'note': row[5],
                'payment_id': row[6],
                'gstamount': row[7],
                'igstamount': row[8],
                'razor_pay_payment_id': row[9],
                
               
            })
    else:
        error_msg = 'Something Went Wrong'
    current_url = request.get_full_path()
    # using the 'current_url' variable to determine the active card.
    # context = {'query_result': data,'current_url': current_url,'error_msg':error_msg}
    return JsonResponse({'data':data,'total_amount':total_amount,'total_gst':total_gst,'total_igst':total_igst,'total_tax':total_tax})
    return render(request, 'payment_pages/payment_receipts.html', {'current_url': current_url,'data':data})


#All Categories
def all_categories(request):
    isLogin = is_loggedin(request)
    if isLogin == False:
        return redirect('dashboard_app:login')
    error_msg = "No Categories Found"
    branch_id = request.session.get('branchid')
    # filter = ''
    # if branch_id :
    #     filter = " and laundry_delivery_boytbl.branchid='"+str(branch_id)+"'"
    query = "select catid,category_name,cat_img,regular_price,regular_price_type,express_price,express_price_type,offer_price,offer_price_type,description from vff.laundry_categorytbl order by catid desc"
    
    query_result = execute_raw_query(query)
    
    
        
    data = []    
    if not query_result == 500:
        for row in query_result:
            
            data.append({
                'catid': row[0],
                'categoryname': row[1],
                'categoryimg': row[2],
                'regular_prize': row[3],
                'regular_prize_type': row[4],
                'express_prize': row[5],
                'express_prize_type': row[6],
                'offer_prize': row[7],
                'offer_prize_type': row[8],
                'description': row[9],
               
            })
    else:
        error_msg = 'Something Went Wrong'
    current_url = request.get_full_path()
    # using the 'current_url' variable to determine the active card.
    context = {'query_result': data,'current_url': current_url,'error_msg':error_msg}
    
    return render(request, 'category_pages/all_categories.html', context)

#Add Category
def add_category(request, catid=None):
    isLogin = is_loggedin(request)
    if isLogin == False:
        return redirect('dashboard_app:login')

    data = {}

    if catid:
        # Fetch existing category data if catid is provided
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT category_name, cat_img,regular_price,regular_price_type,express_price,express_price_type,offer_price,offer_price_type,description FROM vff.laundry_categorytbl WHERE catid='"+str(catid)+"'")
                row = cursor.fetchone()
                if row:
                    data = {
                        'catid': catid,
                        'categoryname': row[0],
                        'categoryimg': row[1],
                        'regular_prize': row[2],
                        'regular_prize_type': row[3],
                        'express_prize': row[4],
                        'express_prize_type': row[5],
                        'offer_prize': row[6],
                        'offer_prize_type': row[7],
                        'description': row[8],
                    }
        except Exception as e:
            print(f"Error loading data: {e}")

    if request.method == "POST":
        categoryname = request.POST.get('categoryname')
        regular_prize = request.POST.get('regular_prize')
        regular_prize_type = request.POST.get('regular_prize_type')
        express_prize = request.POST.get('express_prize')
        express_prize_type = request.POST.get('express_prize_type')
        offer_prize = request.POST.get('offer_prize')
        offer_prize_type = request.POST.get('offer_prize_type')
        description = request.POST.get('description')
        # priority = request.POST.get('priority')
        uploaded_image = request.FILES.get('profile-image1')

        if not offer_prize:
            offer_prize = 0
            offer_prize_type = 'NA'
        if not description:
            description = 'NA'
        if uploaded_image:
            image_url = upload_images2(uploaded_image)
        elif data.get('categoryimg'):
            image_url = data.get('categoryimg')
        else:
            # Handle the case where there's no uploaded image and no previous image
            image_url = ''  # Set it to a default value or handle accordingly

        try:
            with connection.cursor() as cursor:
                if catid:
                    # Update an existing category
                    update_query = (
                        "UPDATE vff.laundry_categorytbl SET category_name='"+str(categoryname)+"', cat_img='"+str(image_url)+"',regular_price='"+str(regular_prize)+"',regular_price_type='"+str(regular_prize_type)+"',express_price='"+str(express_prize)+"',express_price_type='"+str(express_prize_type)+"',offer_price='"+str(offer_prize)+"',offer_price_type='"+str(offer_prize_type)+"',description='"+str(description)+"' WHERE catid='"+str(catid)+"'"
                    )
                    cursor.execute(update_query)
                else:
                    # Insert a new category
                    insert_query = "INSERT INTO vff.laundry_categorytbl (category_name, cat_img,regular_price,regular_price_type,express_price,express_price_type,offer_price,offer_price_type,description) VALUES ('"+str(categoryname)+"', '"+str(image_url)+"','"+str(regular_prize)+"','"+str(regular_prize_type)+"','"+str(express_prize)+"','"+str(express_prize_type)+"','"+str(offer_prize)+"','"+str(offer_prize_type)+"','"+str(description)+"')"
                    cursor.execute(insert_query)

                connection.commit()

                print("Category Added/Updated Successfully.")
                return redirect('dashboard_app:all_categories')
        except Exception as e:
            print(f"Error loading data: {e}")

    return render(request, 'category_pages/add_category.html', {'data': data})

#All Sub-Categories
def all_sub_categories(request,catid,catname):
    isLogin = is_loggedin(request)
    if isLogin == False:
        return redirect('dashboard_app:login')
    error_msg = "No Sub-Categories Found"
    branch_id = request.session.get('branchid')
    if request.method == "POST":
        section_type = request.POST.get('section_type')
        
        print(f"section_type::{section_type}")
        
        if section_type == "All":
            query = "select subcatid,sub_cat_name,sub_cat_img,cost,type,category_name,section_type from vff.laundry_categorytbl,vff.laundry_sub_categorytbl where laundry_categorytbl.catid=laundry_sub_categorytbl.catid and laundry_sub_categorytbl.catid='"+str(catid)+"' order by time_epoch desc"
            query_result = execute_raw_query(query)
         
            data = []    
            if not query_result == 500:
                for row in query_result:
            
                    data.append({
                        'catid':catid,
                        'subcatid':row[0],
                        'sub_cat_name':row[1],
                        'sub_cat_img': row[2],
                        'cost': row[3],
                        'type': row[4],
                        'category_name':row[5],
                        'section_type':row[6]
            
               
                     })
                else:
                    error_msg = 'Something Went Wrong'
                current_url = request.get_full_path()
                # using the 'current_url' variable to determine the active card.    
                context = {'query_result': data,'current_url': current_url,'error_msg':error_msg,'catname':catname,'catid':catid,'selected_section':section_type}
                return render(request, 'category_pages/all_subcategories.html', context)
            
            
        query = "select subcatid,sub_cat_name,sub_cat_img,cost,type,category_name,section_type from vff.laundry_categorytbl,vff.laundry_sub_categorytbl where laundry_categorytbl.catid=laundry_sub_categorytbl.catid and laundry_sub_categorytbl.catid='"+str(catid)+"' and section_type='"+str(section_type)+"' order by time_epoch desc"
        query_result = execute_raw_query(query)
         
        data = []    
        if not query_result == 500:
            for row in query_result:
            
                data.append({
                    'catid':catid,
                    'subcatid':row[0],
                    'sub_cat_name':row[1],
                    'sub_cat_img': row[2],
                    'cost': row[3],
                    'type': row[4],
                    'category_name':row[5],
                    'section_type':row[6]
            
               
                 })
        else:
            error_msg = 'Something Went Wrong'
        current_url = request.get_full_path()
        # using the 'current_url' variable to determine the active card.
        
        context = {'query_result': data,'current_url': current_url,'error_msg':error_msg,'catname':catname,'catid':catid,'selected_section':section_type}
    
        return render(request, 'category_pages/all_subcategories.html', context)
    # filter = ''
    # if branch_id :
    #     filter = " and laundry_delivery_boytbl.branchid='"+str(branch_id)+"'"
    query = "select subcatid,sub_cat_name,sub_cat_img,cost,type,category_name,section_type from vff.laundry_categorytbl,vff.laundry_sub_categorytbl where laundry_categorytbl.catid=laundry_sub_categorytbl.catid and laundry_sub_categorytbl.catid='"+str(catid)+"' order by time_epoch desc"
    query_result = execute_raw_query(query)
         
    data = []    
    if not query_result == 500:
        for row in query_result:
            
            data.append({
                'catid':catid,
                'subcatid':row[0],
                'sub_cat_name':row[1],
                'sub_cat_img': row[2],
                'cost': row[3],
                'type': row[4],
                'category_name':row[5],
                'section_type':row[6]
            
               
            })
    else:
        error_msg = 'Something Went Wrong'
    current_url = request.get_full_path()
    # using the 'current_url' variable to determine the active card.
    context = {'query_result': data,'current_url': current_url,'error_msg':error_msg,'catname':catname,'catid':catid}
    
    return render(request, 'category_pages/all_subcategories.html', context)

#Add Sub-Category
def add_sub_category(request, catid,catname):
    isLogin = is_loggedin(request)
    if isLogin == False:
        return redirect('dashboard_app:login')

    data = {}

    if catid:
        # Fetch existing category data if catid is provided
        try:
            with connection.cursor() as cursor:
                cursor.execute("select subcatid,sub_cat_name,sub_cat_img,cost,type,section_type from vff.laundry_sub_categorytbl where catid='"+str(catid)+"'")
                row = cursor.fetchone()
                if row:
                    data = {
                        'catid': catid,
                        'subcatid':row[0],
                        'sub_cat_name':row[1],
                        'sub_cat_img': row[2],
                        'cost': row[3],
                        'type': row[4],
                        
                    }
        except Exception as e:
            print(f"Error loading data: {e}")

    if request.method == "POST":
        subcategoryname = request.POST.get('subcategoryname')
        cost = request.POST.get('cost')
        ctype = request.POST.get('type')
        # kids_cost = request.POST.get('kids_cost')
        # kids_type = request.POST.get('kids_type')
        section_type = request.POST.get('section_type')
        uploaded_image = request.FILES.get('profile-image1')

        if uploaded_image:
            image_url = upload_images2(uploaded_image)
        elif data.get('sub_cat_img'):
            image_url = data.get('sub_cat_img')
        else:
            # Handle the case where there's no uploaded image and no previous image
            image_url = ''  # Set it to a default value or handle accordingly

        try:
            with connection.cursor() as cursor:
                if catid:
                    
                    # Insert a new sub category
                    insert_query = "insert into vff.laundry_sub_categorytbl (catid,sub_cat_name,sub_cat_img,cost,type,section_type) values ('"+str(catid)+"','"+str(subcategoryname)+"','"+str(image_url)+"','"+str(cost)+"','"+str(ctype)+"','"+str(section_type)+"')"
                    cursor.execute(insert_query)

                connection.commit()

                print("Sub Category Added/Updated Successfully.")
                return redirect(reverse('dashboard_app:all_sub_categories', kwargs={'catid': catid,'catname':catname}))
        except Exception as e:
            print(f"Error loading data: {e}")

    return render(request, 'category_pages/add_subcategory.html', {'data_new': data,'catname':catname})

#Add Sub-Category
def update_sub_category(request, catid,subcatid,catname):
    isLogin = is_loggedin(request)
    if isLogin == False:
        return redirect('dashboard_app:login')

    data = {}
    
    
    if subcatid:
        # Fetch existing category data if catid is provided
        try:
            with connection.cursor() as cursor:
                query = "select subcatid,sub_cat_name,sub_cat_img,cost,type,section_type from vff.laundry_sub_categorytbl where subcatid='"+str(subcatid)+"' "
                cursor.execute(query)
                print(query)
                row = cursor.fetchone()
                if row:
                    data = {
                        
                        'subcatid':row[0],
                        'sub_cat_name':row[1],
                        'sub_cat_img': row[2],
                        'cost': row[3],
                        'type': row[4],
                        'section_type': row[5],
                    }
        except Exception as e:
            print(f"Error loading data: {e}")

    if request.method == "POST":
        subcategoryname = request.POST.get('subcategoryname')
        cost = request.POST.get('cost')
        type = request.POST.get('type')
        # kids_cost = request.POST.get('kids_cost')
        # kids_type = request.POST.get('kids_type')
        section_type = request.POST.get('section_type')
        uploaded_image = request.FILES.get('profile-image1')
        
        if uploaded_image:
            image_url = upload_images2(uploaded_image)
        elif data.get('sub_cat_img'):
            image_url = data.get('sub_cat_img')
        else:
            # Handle the case where there's no uploaded image and no previous image
            image_url = ''  # Set it to a default value or handle accordingly

        try:
            with connection.cursor() as cursor:
                if subcatid:
                    # Update an existing category
                    update_query = (
                        "update vff.laundry_sub_categorytbl set sub_cat_name='"+str(subcategoryname)+"',sub_cat_img='"+str(image_url)+"',cost='"+str(cost)+"',type='"+str(type)+"',section_type='"+str(section_type)+"' where subcatid='"+str(subcatid)+"'"
                    )
                    cursor.execute(update_query)
                

                connection.commit()

                print("Sub Category Added/Updated Successfully.")
                return redirect(reverse('dashboard_app:all_sub_categories', kwargs={'catid': catid,'catname':catname}))
        except Exception as e:
            print(f"Error loading data: {e}")

    return render(request, 'category_pages/add_subcategory.html', {'data': data,'catname':catname})


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

import os
from django.conf import settings
from django.http import JsonResponse

def _upload_image(request):
    if request.method == 'POST' and request.FILES.get('image'):
        image = request.FILES['image']
        # Save the image to the media directory
        image_path = os.path.join(settings.MEDIA_ROOT, 'uploaded_images', image.name)
        with open(image_path, 'wb') as destination:
            for chunk in image.chunks():
                destination.write(chunk)

        # Construct the image URL
        image_url = os.path.join(settings.MEDIA_URL, 'uploaded_images', image.name)

        return JsonResponse({'image_url': image_url})
    else:
        return JsonResponse({'error': 'No image file found.'})


def is_loggedin(request):
    # Check if the session variable 'is_logged_in' exists and is set to True
    print("checking if user has logged in or not")
    return request.session.get('is_logged_in', False)

def branch_selected(request):
    return request.session.get('branch_selected',False)

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
