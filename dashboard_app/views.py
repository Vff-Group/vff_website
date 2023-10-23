from django.shortcuts import render,redirect, reverse
from django.db import connection, DatabaseError
from django.views.decorators.cache import never_cache
from django.contrib.auth import logout
from django.http import HttpResponseServerError,JsonResponse
from colorama import Fore, Style
from django.views.decorators.cache import never_cache
from django.utils import timezone
from datetime import datetime
import pytz
import base64
import os
import uuid
import mimetypes

from PIL import Image  # Pillow library for image processing
# Create your views here.
serverToken="AAAApZY1ur0:APA91bHsk-e3OC5R2vqO7dD0WZp7ifULNzqrUPnQu07et7RLFMWWcwOqY9Bl-9YQWkuXUP5nM7bVMgMP-qKISf9Jcf2ix9j7oOkScq9-3BH0hfCH3nIWgkn4hbnmSLyw4pmq66rMZz8R"

def sendFMCMsg(deviceToken,msg,title,data,requests):
    global serverToken
    deviceToken=deviceToken.replace('__colon__',':')
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'key=' + serverToken,
    }
    body = {
        'notification': {'title': title,
        'body': msg
    },
        'data': data,
        'to':
        deviceToken,
        'priority': 'high',
#   'data': dataPayLoad,
    }
    response = requests.post("https://fcm.googleapis.com/fcm/send",headers = headers, data=json.dumps(body))
    print(response)
    print(response.json())
    print(response.status_code)


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
    print(f'Admin Usrid ::{usrid}')
    query = "select branchtbl.branchid,branch_name,address,branch_type,creation_date,branchtbl.status from vff.branchtbl,vff.admintbl where admintbl.branchid=branchtbl.branchid and branchtbl.owner_id=admintbl.usrid and branchtbl.owner_id='"+str(usrid)+"'"
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
        print(branch_name,branchid)
        # Save the selected branchid and brandname to the session
        request.session['branchid'] = branchid
        request.session['branch_name'] = branch_name
        request.session['branch_selected'] = True
        request.session.save()  # Save the session to persist the changes

        return redirect('dashboard_app:dashboard')
    else:
        return redirect('dashboard_app:all_branches')
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
    
    current_url = request.get_full_path()
    # using the 'current_url' variable to determine the active card.
    return render(request, 'admin_pages/dashboard.html', {'current_url': current_url})
    
    
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
    query = " select laundry_customertbl.usrid,usrname,mobile_no,usertbl.address,lat,lng,age,gender,laundry_customertbl.branchid,consmrid,laundry_customertbl.status,is_online,usertbl.epoch,profile_img from vff.laundry_customertbl,vff.usertbl where laundry_customertbl.usrid=usertbl.usrid order by usrname desc"
    
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
                cursor.execute("select usrname,mobile_no,usertbl.address,age,gender,consmrid,landmark,date_of_birth,pincode,query,profile_img"
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
        if errors:
            # If there are validation errors, render the form with error messages
            return render(request, 'delivery_agents_pages/add_new_delivery_agent.html', {'errors': errors})
        
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
                        "update vff.laundry_customertbl set customer_name='"+str(uname)+"', query='"+str(queries)+"' where usrid='"+str(usrid)+"'"
                    )
                    print(f"update customer details::{update_customer}")
                    cursor.execute(update_customer)
                else:
                    # Insert a new customers
                    usertbl_query = "insert into vff.usertbl (usrname,mobile_no,address,age,gender,date_of_birth,pincode,landmark,profile_img) VALUES ('"+str(uname)+"', '"+str(primary_mobno)+"', '"+str(address)+"','"+str(age)+"','"+str(gender)+"','"+str(date_of_birth)+"','"+str(pincode)+"','"+str(land_mark)+"','"+str(image_url)+"') RETURNING usrid"
                    cursor.execute(usertbl_query)
                    usrid = cursor.fetchone()[0]  # Retrieve the returned usrid

                    insert_query = (
                        "insert into vff.laundry_customertbl (usrid,branchid,customer_name,query) values "
                        "('"+str(usrid)+"','"+str(branch_id)+"','"+str(uname)+"','"+str(queries)+"')"
                        
                    )
                    print(f"Create New user details::{insert_query}")
                    cursor.execute(insert_query)
                connection.commit()

                print("Customer Added/Updated Successfully.")
                return redirect('dashboard_app:customers')
        except Exception as e:
            print(f"Error loading data: {e}")

    
    
    return render(request,'customer_pages/add_customer.html',{'data':data})


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

#All Orders
def all_orders(request):
    isLogin = is_loggedin(request)
    if isLogin == False:
        return redirect('dashboard_app:login')
    error_msg = "No Orders Data Found"
    query = "select consmrid,usertbl.usrid,customer_name,mobile_no,houseno,address,city,pincode,landmark,profile_img,device_token,orderid,delivery_boyid,quantity,price,pickup_dt,delivery,clat,clng,order_completed,order_status,additional_instruction,laundry_ordertbl.epoch,cancel_reason,feedback,delivery_epoch,name as deliveryboy_name from vff.laundry_ordertbl,vff.laundry_customertbl,vff.usertbl,vff.laundry_delivery_boytbl where laundry_customertbl.usrid=usertbl.usrid and laundry_ordertbl.customerid=laundry_customertbl.consmrid and laundry_ordertbl.delivery_boyid=laundry_delivery_boytbl.delivery_boy_id order by orderid desc"
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
    query = "select consmrid,usertbl.usrid,customer_name,mobile_no,houseno,address,city,pincode,landmark,profile_img,device_token,orderid,delivery_boyid,quantity,price,pickup_dt,delivery,clat,clng,order_completed,order_status,additional_instruction,laundry_ordertbl.epoch,cancel_reason,feedback,delivery_epoch,name as deliveryboy_name,categoryid,subcategoryid,ordertype,dt,cat_img,cat_name,sub_cat_name,sub_cat_img,actual_cost,time,item_cost,item_quantity,type,section_type from vff.laundry_active_orders_tbl,vff.laundry_ordertbl,vff.laundry_customertbl,vff.usertbl,vff.laundry_delivery_boytbl where laundry_customertbl.usrid=usertbl.usrid and laundry_ordertbl.customerid=laundry_customertbl.consmrid and laundry_ordertbl.delivery_boyid=laundry_delivery_boytbl.delivery_boy_id and laundry_active_orders_tbl.order_id=laundry_ordertbl.orderid and orderid='"+str(orderid)+"' order by orderid desc;"
    
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
                
                
               
            })
        
        #Payment Details
        payment_id = 'Payment Not Done'
        query_payment = "select razor_pay_payment_id,status,time,dt from vff.laundry_payment_tbl where order_id='"+str(orderid)+"'"
        pay_result = execute_raw_query_fetch_one(query_payment)
        if pay_result:   
            payment_id = pay_result[0]
        
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
        delivery_query = "select price  from vff.laundry_delivery_chargetbl"
        dlvrych_result = execute_raw_query_fetch_one(delivery_query)
        if dlvrych_result:   
            delivery_price = dlvrych_result[0]
        
        extra_item_sum = sum(extra['extra_item_price'] for extra in extra_data)

        total_laundry_cost = sum(item['item_cost'] for item in data)
        print(f'total_laundry_cost::{total_laundry_cost}')
        print(f'extra_item_sum::{extra_item_sum}')
        print(f'delivery_price::{delivery_price}')
        
        if total_laundry_cost != 0:
            if total_laundry_cost < delivery_price:
                total_laundry_cost += delivery_price
            else:
                delivery_price = 0
        
        total_cost = total_laundry_cost + extra_item_sum
        print(f'total_cost::{total_cost}')
        first_order_id = data[0]['orderid'] if data else ''
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
        request.session['order_id'] = first_order_id
        order_completed_status = ""
        if order_completed == 0:
            order_completed_status = "Accepted"
        elif order_completed == 1:
            order_completed_status = "Completed"
        elif order_completed_status == 2:
            order_completed_status = "Cancelled"
            
        print(f'OrderID::{first_order_id}')
        
    else:
        error_msg = 'Something Went Wrong'
       
    context ={'query_result':data,'extra_data':extra_data,'error_msg':error_msg,'payment_id':payment_id,'order_id':first_order_id,'customer_name':customer_name
              ,'address':address,'houseno':houseno,'city':city,'pincode':pincode,'landmark':landmark,'order_status':order_status,'order_completed_status':order_completed_status,'order_date':order_date,'delivery_date':delivery_date,'extra_item_sum':extra_item_sum,'delivery_price':delivery_price,'total_cost':total_cost,'extra_error':extra_error}
    
    return render(request,'order_pages/order_details.html',context)

def update_order_status(request,order_id):
    if request.method == "POST":
        order_status = request.POST.get('order-status')
        # order_id = request.session.get('order_id')
        userid = request.session.get('userid')
        order_completed  = "0"
        if order_status == "Completed":
            order_completed = "1"
        elif order_status == "Cancelled":
            order_completed = "2"
        else:
            order_completed = "0"
        if order_status == "Out for Delivery":
            query_token = "select usrname,mobile_no,device_token,delivery_boy_id from vff.usertbl,vff.laundry_delivery_boytbl,vff.laundry_ordertbl where usertbl.usrid=laundry_delivery_boytbl.usrid and laundry_ordertbl.delivery_boyid=laundry_delivery_boytbl.delivery_boy_id and orderid='"+str(order_id)+"'"
            token_result = execute_raw_query_fetch_one(query_token)
            if token_result:   
                delivery_boy_id = token_result[3]
                device_token = token_result[2]
                
                
                title = "VFF Group"
                msg = "Delivery Package is ready pick it up from store"
                data = {
                         'intent':'DMainRoute',
                         
                         }
                sendFMCMsg(device_token,msg,title,data,request)
        try:
            with connection.cursor() as cursor:
                
                query = "update vff.laundry_ordertbl set order_status='"+str(order_status)+"',order_completed='"+str(order_completed)+"' where orderid='"+str(order_id)+"'"
                cursor.execute(query)
                connection.commit()
                query2 = "insert into vff.laundry_order_historytbl(order_id,order_stages) values ('"+str(order_id)+"','"+str(order_status)+"')"
                cursor.execute(query2)
                connection.commit()
                insert_notify="insert into vff.laundry_notificationtbl(title,body,reciever_id,sender_id,order_id) values ('"+str(title)+"','"+str(msg)+"','"+str(delivery_boy_id)+"','"+str(userid)+"','"+str(order_id)+"')"
                cursor.execute(insert_notify)
                connection.commit()
                print("Order Status Updated Successfully")
                return redirect(reverse('dashboard_app:view_order_detail', kwargs={'orderid': order_id}))
        except Exception as e:
            print(f"Error loading data: {e}")
    return redirect(reverse('dashboard_app:view_order_detail', kwargs={'orderid': order_id}))
            
        
        
        
        
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
    query = "select catid,category_name,cat_img,regular_price,regular_price_type,express_price,express_price_type,offer_price,offer_price_type,description from vff.laundry_categorytbl order by priority"
    
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
