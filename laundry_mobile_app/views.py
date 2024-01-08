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
from django.views.decorators.csrf import csrf_exempt

# Create your views here.
reply_data = ''
serverToken="AAAApZY1ur0:APA91bHsk-e3OC5R2vqO7dD0WZp7ifULNzqrUPnQu07et7RLFMWWcwOqY9Bl-9YQWkuXUP5nM7bVMgMP-qKISf9Jcf2ix9j7oOkScq9-3BH0hfCH3nIWgkn4hbnmSLyw4pmq66rMZz8R"

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


def execute_query_and_get_result(query):
    global reply_data 
    qtype=0
    if ("returning" in query) and ("insert" in query):
        qtype=1
    elif  ("insert" in query) or ("delete" in query) or ("update" in query):
        qtype=2
 #   print('qtype->'+str(qtype))
    
    with connection.cursor() as cursor:
        try:
                print(f"{Fore.GREEN}Query Executed: {query}{Style.RESET_ALL}")
   #             print(cur)
                reply_data="ErrorCode#0"
                cursor.execute(query) #exception should be handled
                if qtype == 2:
                    connection.commit()
                    return None
                elif qtype == 1:
                    connection.commit()
        except Exception as e:
            print(f"{Fore.RED}Query Execution Error:: {e}{Style.RESET_ALL}")
            reply_data="ErrorCode#8"
            return None
    
        recs=cursor.fetchall()
        rows=len(recs)
        print(f"{Fore.YELLOW}==** Selected ROWS : {rows} **==")
        if len(recs) ==0 :
            reply_data="ErrorCode#2"
            print('Error Code 2')
            return None
        cols=len(recs[0])
        retMap={}
        i=0
        while i<cols:
            j=0
            lst=[]
            while j<rows:
                val=recs[j][i]
                lst.append(str(val))
                j=j+1
            i=i+1
            retMap[str(i)]=lst
    return retMap

def lst_to_str(lst):
    return ",".join([str(i).replace(","," ") for i in lst if i])

@csrf_exempt
def login(request):
    global reply_data 
    if request.method == "POST":
        # Parsing and printing JSON body
        try:
            jdict = json.loads(request.body)
            mobno = jdict['mobno']
            email = jdict['email_id']
            uname = jdict['usrname']
            lat = jdict['lat']
            lng = jdict['lng']
            token = jdict['user_token']
            profile_img = jdict['profile_img']
            print(f'username:{uname}')
            if uname == '':
                uname = 'Apple User'
            query = "select usertbl.usrid,usrname,consmrid,gender,token,created_date,profile_img,email from vff.laundry_customertbl,vff.usertbl where laundry_customertbl.usrid=usertbl.usrid and mobile_no='"+str(mobno)+"'"
            if query != "":
                reply_data = "ErrorCode#0"
                mapVal = execute_query_and_get_result(query)
                if mapVal == None and reply_data == "ErrorCode#2":
                    query = "insert into vff.usertbl (usrname,mobile_no,token,email,profile_img,lat,lng) values ('"+str(uname)+"','"+str(mobno)+"','"+str(token)+"','"+str(email)+"','"+str(profile_img)+"','"+str(lat)+"','"+str(lng)+"') returning usrid"
                    print('creating new user query--> '+str(query))
                    try:
                        with connection.cursor() as cursor:
                            cursor.execute(query)
                            connection.commit()
                            data=cursor.fetchall()
                            if len(data) !=0:
                                rusrid=str(data[0][0])
                                print('----------Returning Usrid-----> '+str(rusrid))
                            if rusrid != "":
                                query="insert into vff.laundry_customertbl (usrid,customer_name,is_online) values ('"+str(rusrid)+"','"+str(uname)+"','1')"
                                try:
                                    cursor.execute(query)
                                    connection.commit()
                                    query = "select usertbl.usrid,usrname,consmrid,gender,token,created_date,profile_img,email from vff.laundry_customertbl,vff.usertbl where laundry_customertbl.usrid=usertbl.usrid and mobile_no='"+str(mobno)+"'"
                                    reply_data="ErrorCode#0"
                                    mapVal = execute_query_and_get_result(query)
                                    if mapVal != None:
                                    
                                        usrid = mapVal["1"]
                                        usrname=mapVal["2"]
                                        customerid=mapVal["3"]
                                        gender=mapVal["4"]
                                        token=mapVal["5"]
                                        created_dt=mapVal["6"]
                                        profile_img=mapVal["7"]
                                        email=mapVal["8"]

                                        usridstr = lst_to_str(usrid)
                                        usrnamestr = lst_to_str(usrname)
                                        customer_idstr = lst_to_str(customerid)
                                        genderstr = lst_to_str(gender)
                                        tokenstr = lst_to_str(token)
                                        created_atstr = lst_to_str(created_dt)
                                        profile_imgstr = lst_to_str(profile_img)
                                        email_str = lst_to_str(email)

                                        jdict={
                                            "usrid":str(usridstr),
                                            "usrname":str(usrnamestr),
                                            "customer_id":str(customer_idstr),
                                            "gender":str(genderstr),
                                            "user_token":str(tokenstr),
                                            "created_at":str(created_atstr),
                                            "profile_img":str(profile_imgstr),
                                            "email":str(email_str),
                                            }
                                        
                                        # Returning the data as a JSON response
                                        return JsonResponse(jdict, safe=False)#safe because jdict is already serialized and to avoid dict confusion

                                except Exception as e:
                                    print(e)
                                    reply_data="ErrorCode#8"
                    except Exception as e:
                        print(e)
                        reply_data="ErrorCode#8"

                if mapVal != None:
                    usrid = mapVal["1"]
                    usrname=mapVal["2"]
                    customerid=mapVal["3"]
                    gender=mapVal["4"]
                    token=mapVal["5"]
                    created_dt=mapVal["6"]
                    profile_img=mapVal["7"]
                    email=mapVal["8"]

                    usridstr = lst_to_str(usrid)
                    usrnamestr = lst_to_str(usrname)
                    customer_idstr = lst_to_str(customerid)
                    genderstr = lst_to_str(gender)
                    tokenstr = lst_to_str(token)
                    created_atstr = lst_to_str(created_dt)
                    profile_imgstr = lst_to_str(profile_img)
                    email_str = lst_to_str(email)


                    jdict={
                        "usrid":str(usridstr),
                        "usrname":str(usrnamestr),
                        "customer_id":str(customer_idstr),
                        "gender":str(genderstr),
                        "user_token":str(tokenstr),
                        "created_at":str(created_atstr),
                        "profile_img":str(profile_imgstr),
                        "email":str(email_str),
                        }
                    print(jdict)
                    
                    # Returning the data as a JSON response
                    return JsonResponse(jdict, safe=False)#safe because jdict is already serialized and to avoid dict confusion
        except KeyError as e:
            print(f"{Fore.RED}KeyError: {e}{Style.RESET_ALL} - Key does not exist in the JSON")
            return JsonResponse('ErrorCode#8',safe=False)
        except json.JSONDecodeError as e:
            print(f"{Fore.RED}Failed to parse JSON: {e}{Style.RESET_ALL}")
            return JsonResponse('ErrorCode#8',safe=False)
        except Exception as ex:
            print(f"{Style.RESET_ALL}Error fetching data: {ex}{Style.RESET_ALL}")
            return JsonResponse('ErrorCode#8',safe=False)

    return JsonResponse(reply_data,safe=False)

@csrf_exempt
def load_laundry_all_categories(request):
    global reply_data 
    reply_data = 'ErrorCode#0'
    if request.method == "POST":
        try:
            jdict = json.loads(request.body)
            query = "select catid,category_name,cat_img,regular_price,regular_price_type,express_price,express_price_type,offer_price,offer_price_type,description,min_hours from vff.laundry_categorytbl order by category_name "

            if query != "":
                reply_data="ErrorCode#0"
                mapVal = execute_query_and_get_result(query)
                if mapVal != None:
                    catid=mapVal["1"]
                    catName=mapVal["2"]
                    catImg=mapVal["3"]
                    reg_price=mapVal["4"]
                    reg_price_type=mapVal["5"]
                    exp_price=mapVal["6"]
                    exp_price_type=mapVal["7"]
                    offer_price=mapVal["8"]
                    offer_price_type=mapVal["9"]
                    desc=mapVal["10"]
                    min_hours=mapVal["11"]

                    catidstr=lst_to_str(catid)
                    catnamestr=lst_to_str(catName)
                    catimgstr=lst_to_str(catImg)
                    reg_pricestr=lst_to_str(reg_price)
                    reg_price_typestr=lst_to_str(reg_price_type)
                    exp_pricestr=lst_to_str(exp_price)
                    exp_price_typestr=lst_to_str(exp_price_type)
                    offer_pricestr=lst_to_str(offer_price)
                    offer_price_typestr=lst_to_str(offer_price_type)
                    descstr=lst_to_str(desc)
                    min_hoursstr=lst_to_str(min_hours)

                    jdict={
                            "catid":str(catidstr),
                            "catname":str(catnamestr),
                            "catimg":str(catimgstr),
                            "regular_price":str(reg_pricestr),
                            "regular_price_type":str(reg_price_typestr),
                            "express_price":str(exp_pricestr),
                            "express_price_type":str(exp_price_typestr),
                            "offer_price":str(offer_pricestr),
                            "offer_price_type":str(offer_price_typestr),
                            "description":str(descstr),
                            "catname":str(catnamestr),
                            "catname":str(catnamestr),
                            "min_hours":str(min_hoursstr),
                            }
                    
                    return JsonResponse(jdict,safe=False)
        except KeyError as e:
            print(f"{Fore.RED}KeyError: {e}{Style.RESET_ALL} - Key does not exist in the JSON")
            return JsonResponse('ErrorCode#8',safe=False)
        except json.JSONDecodeError as e:
            print(f"{Fore.RED}Failed to parse JSON: {e}{Style.RESET_ALL}")
            return JsonResponse('ErrorCode#8',safe=False)
        except Exception as ex:
            print(f"{Style.RESET_ALL}Error fetching data: {ex}{Style.RESET_ALL}")
            return JsonResponse('ErrorCode#8',safe=False)

    return JsonResponse(reply_data,safe=False)


@csrf_exempt
def load_laundry_customer_address(request):
    global reply_data
    reply_data = 'ErrorCode#2'
    if request.method == "POST":
        try:
            jdict = json.loads(request.body)
            usrid = jdict['usrid']
            query = "select houseno,address,city,pincode,landmark from vff.usertbl where usrid='"+str(usrid)+"'"
            if query != "":
                reply_data = "ErrorCode#0"
            mapVal = execute_query_and_get_result(query)

            if mapVal != None:
                buildingNo = mapVal["1"]
                streetAddress=mapVal["2"]
                cityName=mapVal["3"]
                zipCode=mapVal["4"]
                landMark=mapVal["5"]
                buildingno_str = lst_to_str(buildingNo)
                street_str = lst_to_str(streetAddress)
                cityname_str = lst_to_str(cityName)
                zipcode_str = lst_to_str(zipCode)
                landmark_str = lst_to_str(landMark)

                jdict={
                        'buildingNo':str(buildingno_str),
                        'streetAddress':str(street_str),
                        'cityName':str(cityname_str),
                        'zipCode':str(zipcode_str),
                        'landMark':str(landmark_str),

                }
                return JsonResponse(jdict,safe=False)
        except KeyError as e:
            print(f"{Fore.RED}KeyError: {e}{Style.RESET_ALL} - Key does not exist in the JSON")
            return JsonResponse('ErrorCode#8',safe=False)
        except json.JSONDecodeError as e:
            print(f"{Fore.RED}Failed to parse JSON: {e}{Style.RESET_ALL}")
            return JsonResponse('ErrorCode#8',safe=False)
        except Exception as ex:
            print(f"{Style.RESET_ALL}Error fetching data address: {ex}{Style.RESET_ALL}")
            return JsonResponse('ErrorCode#8',safe=False)

    return JsonResponse(reply_data,safe=False)

@csrf_exempt
def request_pickup_laundry_customer(request):
    global reply_data
    if request.method == "POST":
        try:
            jdict=json.loads(request.body)
            buildingNo = jdict['buildingNo']
            streetAddress = jdict['streetAddress']
            cityName = jdict['cityName']
            zipCode= jdict['zipCode']
            landMark = jdict['landMark']
            customerId = jdict['customerId']
            customer_usrid = jdict['customerUsrid']
            clat = jdict['clat']
            clng = jdict['clng']
            branch_id = jdict['branch_id']
            query = "update vff.usertbl set houseno='"+str(buildingNo)+"',address='"+str(streetAddress)+"',city='"+str(cityName)+"',pincode='"+str(zipCode)+"',landmark='"+str(landMark)+"' where usrid='"+str(customer_usrid)+"'"
             #query2 = "insert into vff.laundry_ordertbl(customerid,clat,clng) values ("+str(customerId)+","+str(clat)+","+str(clng)+") returning orderid";
            query2="insert into vff.laundry_order_bookingtbl(customerid,address,city,pincode,landmark,clat,clng,branch_id) values ('"+str(customerId)+"','"+str(streetAddress)+"','"+str(cityName)+"','"+str(zipCode)+"','"+str(landMark)+"',"+str(clat)+","+str(clng)+",'"+str(branch_id)+"') returning bookingid"
            with connection.cursor() as cursor:
                cursor.execute(query)
                connection.commit()
                reply_data="ErrorCode#0"
                try:
                    cursor.execute(query2)
                    connection.commit()
                    data = cursor.fetchall()
                    if len(data) !=0:
                        booking_id=str(data[0][0])
                        print('----------Returning Booking ID-----> '+str(booking_id))
                        title ="VFF Group"
                        body = "Customer Pickup Request For Booking ID #"+str(booking_id)+""
                        intent="DMainRoute"
                        mdata = {
                             'intent':'DMainRoute',
                            'booking_id':str(booking_id)
                             }
                        send_notification_to_delivery_boy(request,booking_id,customer_usrid,title,body,intent,mdata,branch_id)
                        reply_data="ErrorCode#0"
                except Exception as e:
                    print(e)
                    reply_data = "ErrorCode#8"
        except KeyError as e:
            print(f"{Fore.RED}KeyError: {e}{Style.RESET_ALL} - Key does not exist in the JSON")
            return JsonResponse('ErrorCode#8',safe=False)
        except json.JSONDecodeError as e:
            print(f"{Fore.RED}Failed to parse JSON: {e}{Style.RESET_ALL}")
            return JsonResponse('ErrorCode#8',safe=False)
        except Exception as ex:
            print(f"{Style.RESET_ALL}Error fetching data: {ex}{Style.RESET_ALL}")
            return JsonResponse('ErrorCode#8',safe=False)

    return JsonResponse('ErrorCode#8',safe=False)


@csrf_exempt
def update_user_device_token(request):
    global reply_data
    if request.method == "POST":
        try:
            jdict=json.loads(request.body)
            deviceToken = jdict['deviceToken']
            usrid = jdict['usrid']


            query = "update vff.usertbl set  device_token='"+str(deviceToken)+"' where usrid='"+str(usrid)+"'"
            try:
                with connection.cursor() as cursor:
                    cursor.execute(query)
                    connection.commit()
                    reply_data="ErrorCode#0"
                    
            except Exception as e:
                print(e)
                reply_data ="ErrorCode#8"
                
        except KeyError as e:
            print(f"{Fore.RED}KeyError: {e}{Style.RESET_ALL} - Key does not exist in the JSON")
            return JsonResponse('ErrorCode#8',safe=False)
        except json.JSONDecodeError as e:
            print(f"{Fore.RED}Failed to parse JSON: {e}{Style.RESET_ALL}")
            return JsonResponse('ErrorCode#8',safe=False)
        except Exception as ex:
            print(f"{Style.RESET_ALL}Error fetching data: {ex}{Style.RESET_ALL}")
            return JsonResponse('ErrorCode#8',safe=False)

    return JsonResponse(reply_data,safe=False)


@csrf_exempt
def delivery_boy_login(request):
    global reply_data
    
    if request.method == "POST":
        try:
            jdict = json.loads(request.body)
            username = jdict['username']
            password = jdict['password']
            notificationToken = jdict['notificationToken']

            query = "select usertbl.usrid,usrname,mobile_no,profile_img,device_token,delivery_boy_id,branchid from vff.laundry_delivery_boytbl,vff.usertbl where usertbl.usrid=laundry_delivery_boytbl.usrid and username='"+str(username)+"' and password='"+str(password)+"'"

            if query != "":
                reply_data="ErrorCode#0"
                mapVal = execute_query_and_get_result(query)
                if mapVal != None:
                    usrid=mapVal["1"]
                    usrname=mapVal["2"]
                    mobno=mapVal["3"]
                    profile_img=mapVal["4"]
                    device_token=mapVal["5"]
                    delivery_boy_id=mapVal["6"]
                    branchid=mapVal["7"]
                    query2 = "update vff.usertbl set  device_token='"+str(notificationToken)+"' where usrid='"+str(usrid[0])+"'"
                    try:
                        with connection.cursor() as cursor:
                            cursor.execute(query2)
                            connection.commit()
                    except Exception as e:
                        print('Failed Updating delivery Boy Token');
                        print(e)
                    usrid_str=lst_to_str(usrid)
                    usrname_str=lst_to_str(usrname)
                    mobno_str=lst_to_str(mobno)
                    profile_img_str=lst_to_str(profile_img)
                    device_token_str=lst_to_str(device_token)
                    delivery_boy_id_str=lst_to_str(delivery_boy_id)
                    branchid_str=lst_to_str(branchid)

                    jdict={
                            "usrid":str(usrid_str),
                            "usrname":str(usrname_str),
                            "mobno":str(mobno_str),
                            "profile_img":str(profile_img_str),
                            "device_token":str(device_token_str),
                            "delivery_boy_id":str(delivery_boy_id_str),
                            "branchid":str(branchid_str),
                            }
                    return JsonResponse(jdict,safe=False)
        except KeyError as e:
            print(f"{Fore.RED}KeyError: {e}{Style.RESET_ALL} - Key does not exist in the JSON")
            return JsonResponse('ErrorCode#8',safe=False)
        except json.JSONDecodeError as e:
            print(f"{Fore.RED}Failed to parse JSON: {e}{Style.RESET_ALL}")
            return JsonResponse('ErrorCode#8',safe=False)
        except Exception as ex:
            print(f"{Style.RESET_ALL}Error fetching data: {ex}{Style.RESET_ALL}")
            return JsonResponse('ErrorCode#8',safe=False)

    return JsonResponse(reply_data,safe=False)


@csrf_exempt
#Loading Notification new orders for delivery to accept or reject the order using orderid 
def load_new_orders_requested_to_delivery_boy(request):
    global reply_data
    reply_data="ErrorCode#2"
    if request.method == "POST":
        try:
            jdict = json.loads(request.body)
            booking_id = jdict['booking_id']
            branch_id = jdict['branch_id']

            query="select bookingid,customerid,address,city,pincode,landmark,clat,clng,time_at,customer_name from vff.laundry_order_bookingtbl,vff.laundry_customertbl where laundry_order_bookingtbl.customerid=laundry_customertbl.consmrid and delivery_boy_id='-1' and bookingid='"+str(booking_id)+"' and branch_id='"+str(branch_id)+"'"
            if query != "":
                reply_data="ErrorCode#0"
                mapVal = execute_query_and_get_result(query)
                if mapVal != None:
                    bookingid=mapVal["1"]
                    customerid=mapVal["2"]
                    address=mapVal["3"]
                    city=mapVal["4"]
                    pincode=mapVal["5"]
                    landmark=mapVal["6"]
                    clat=mapVal["7"]
                    clng=mapVal["8"]
                    time_at=mapVal["9"]
                    customer_name=mapVal["10"]

                    bookingid_str=lst_to_str(bookingid)
                    customerid_str=lst_to_str(customerid)
                    address_str=lst_to_str(address)
                    city_str=lst_to_str(city)
                    pincode_str=lst_to_str(pincode)
                    landmark_str=lst_to_str(landmark)
                    clat_str=lst_to_str(clat)
                    clng_str=lst_to_str(clng)
                    time_at_str=lst_to_str(time_at)
                    customer_name_str=lst_to_str(customer_name)

                    jdict={
                            "bookingid":str(bookingid_str),
                            "customerid":str(customerid_str),
                            "address":str(address_str),
                            "city":str(city_str),
                            "pincode":str(pincode_str),
                            "landmark":str(landmark_str),
                            "clat":str(clat_str),
                            "clng":str(clng_str),
                            "time_at":str(time_at_str),
                            "customer_name":str(customer_name_str),
                            }
                    return JsonResponse(jdict,safe=False)
        except KeyError as e:
            print(f"{Fore.RED}KeyError: {e}{Style.RESET_ALL} - Key does not exist in the JSON")
            return JsonResponse('ErrorCode#8',safe=False)
        except json.JSONDecodeError as e:
            print(f"{Fore.RED}Failed to parse JSON: {e}{Style.RESET_ALL}")
            return JsonResponse('ErrorCode#8',safe=False)
        except Exception as ex:
            print(f"{Style.RESET_ALL}Error fetching data: {ex}{Style.RESET_ALL}")
            return JsonResponse('ErrorCode#8',safe=False)

    return JsonResponse(reply_data,safe=False)



@csrf_exempt
def accept_or_reject_order_delivery_boy(request):
    global reply_data
    if request.method == "POST":
        try:
            jdict=json.loads(request.body)
            booking_id = jdict['booking_id']
            branch_id = jdict['branch_id']
            delivery_boy_id = jdict['delivery_boy_id']
            status = jdict['status']#Accepted or Rejected
            print(f'booking_accept_status::{status}')

            query = "insert into vff.laundry_delivery_accept_tbl(delivery_boy_id,status,booking_id,branch_id) values ('"+str(delivery_boy_id)+"','"+str(status)+"','"+str(booking_id)+"','"+str(branch_id)+"')"
            
            try:
                with connection.cursor() as cursor:
                    cursor.execute(query)
                    connection.commit()
                    reply_data="ErrorCode#0"
                    if status !='Rejected':
                        query2="update vff.laundry_order_bookingtbl set delivery_boy_id='"+str(delivery_boy_id)+"',booking_status='"+str(status)+"' where bookingid='"+str(booking_id)+"'"
                        try:
                            with connection.cursor() as cursor:
                                cursor.execute(query2)
                                connection.commit()
                                reply_data="ErrorCode#0"

                                query3="update vff.laundry_delivery_boytbl set status='Busy' where delivery_boy_id='"+str(delivery_boy_id)+"'"
                            try:
                                with connection.cursor() as cursor:
                                    cursor.execute(query3)
                                    connection.commit()
                                    reply_data="ErrorCode#0"
                            except Exception as e:
                                print(e)
                                reply_data="ErrorCode#8"

                            #Order Assignment
                            if status !='Rejected':
                                query5="insert into vff.laundry_order_assignmenttbl(booking_id,delivery_boy_id,type_of_order) values ('"+str(booking_id)+"','"+str(delivery_boy_id)+"','Pickup')"
                                try:
                                    with connection.cursor() as cursor:
                                        cursor.execute(query5)
                                        connection.commit()
                                        reply_data="ErrorCode#0"
                                except Exception as e:
                                    print(e)
                                    reply_data="ErrorCode#8"

                        except Exception as e:
                            print(e)
                            reply_data = "ErrorCode#8"
                    if status == 'Rejected':
                        print('------------------------------------ Important ------------------------------')
                        print('Need to Send to Dashboard as Notification saying pickup request rejected here')
                        title='Pickup Rejected'
                        body='Pickup Rejected for Booking ID #'+str(booking_id)
                        intent='MainRoute'
                        mdata = {
                                     'intent':'DMainRoute',
                                    'booking_id':str(booking_id)
                                     }
                        send_notification_to_dashboard(request,booking_id,'1',title,body,intent,mdata,branch_id,delivery_boy_id)
                        query4 = "update vff.laundry_delivery_boytbl set status='Free'  where delivery_boy_id='"+str(delivery_boy_id)+"'"
                        try:
                            with connection.cursor() as cursor:
                                cursor.execute(query4)
                                connection.commit()
                                reply_data="ErrorCode#0"
                        except Exception as e:
                            print(e)
                            reply_data="ErrorCode#8"
        
            except Exception as ee:
                print(ee)
                return JsonResponse('ErrorCode#8',safe=False)
        except KeyError as e:
            print(f"{Fore.RED}KeyError: {e}{Style.RESET_ALL} - Key does not exist in the JSON")
            return JsonResponse('ErrorCode#8',safe=False)
        except json.JSONDecodeError as e:
            print(f"{Fore.RED}Failed to parse JSON: {e}{Style.RESET_ALL}")
            return JsonResponse('ErrorCode#8',safe=False)
        except Exception as ex:
            print(f"{Style.RESET_ALL}Error fetching data: {ex}{Style.RESET_ALL}")
            return JsonResponse('ErrorCode#8',safe=False)

    return JsonResponse(reply_data,safe=False)


'''
Loading Customer Orders recent here
Loads only if Delivery Boy Accepts the Order
Order Complete Status Goes Like this
0 - Not Completed
1 - Completed
2 - Cancelled
'''
@csrf_exempt
def load_customer_new_orders(request):
    global reply_data
    if request.method == "POST":
        try:
            
            jdict = json.loads(request.body)
            customer_id = jdict['customer_id']
            key = jdict['key']
            if key == 1:
                query_orders="select orderid,epoch,pickup_dt,clat,clng,customer_name,laundry_customertbl.usrid,delivery_boyid,name as delivery_boy_name,order_status,laundry_ordertbl.branch_id from vff.laundry_delivery_boytbl,vff.laundry_customertbl,vff.laundry_ordertbl where laundry_customertbl.consmrid=laundry_ordertbl.customerid and laundry_delivery_boytbl.delivery_boy_id=laundry_ordertbl.delivery_boyid  and laundry_ordertbl.customerid='"+str(customer_id)+"' and order_completed='0' order by orderid desc"
                if query_orders !="":
                    reply_data="ErrorCode#0"
                    mapVal = execute_query_and_get_result(query_orders)
                    if mapVal != None:
                        orderid=mapVal["1"]
                        epoch=mapVal["2"]
                        pickup_dt=mapVal["3"]
                        clat=mapVal["4"]
                        clng=mapVal["5"]
                        customer_name=mapVal["6"]
                        cusrid=mapVal["7"]
                        delivery_boy_id=mapVal["8"]
                        delivery_boy_name=mapVal["9"]
                        order_status=mapVal["10"]
                        branch_id=mapVal["11"]

                        orderid_str=lst_to_str(orderid)
                        epoch_str=lst_to_str(epoch)
                        pickup_dt_str=lst_to_str(pickup_dt)
                        clat_str=lst_to_str(clat)
                        clng_str=lst_to_str(clng)
                        customer_name_str=lst_to_str(customer_name)
                        customer_usrid_str=lst_to_str(cusrid)
                        delivery_boy_id_str=lst_to_str(delivery_boy_id)
                        delivery_boy_name_str=lst_to_str(delivery_boy_name)
                        order_status_str=lst_to_str(order_status)
                        branch_id_str=lst_to_str(branch_id)


                        jdict={
                                "order_id":str(orderid_str),
                                "epoch":str(epoch_str),
                                "pickup_dt":str(pickup_dt_str),
                                "clat":str(clat_str),
                                "clng":str(clng_str),
                                "customer_name":str(customer_name_str),
                                "customer_usrid":str(customer_usrid_str),
                                "delivery_boy_id":str(delivery_boy_id_str),
                                "delivery_boy_name":str(delivery_boy_name_str),
                                "order_status":str(order_status_str),
                                "branch_id":str(branch_id_str),
                            }
                        
                        return JsonResponse(jdict,safe=False)


            else:
                query = "select bookingid,laundry_order_assignmenttbl.delivery_boy_id,booking_status,time_at,branch_id from vff.laundry_order_bookingtbl,vff.laundry_order_assignmenttbl where laundry_order_bookingtbl.bookingid=laundry_order_assignmenttbl.booking_id and customerid='"+str(customer_id)+"' and (booking_status='NA' or booking_status='Accepted') and order_id='-1' order by bookingid desc"
                if query != "":
                    reply_data="ErrorCode#0"
                    mapVal = execute_query_and_get_result(query)
                    if mapVal != None:
                        bookingid=mapVal["1"]
                        delivery_boy_id=mapVal["2"]
                        booking_status=mapVal["3"]
                        time_at=mapVal["4"]
                        branch_id=mapVal["5"]

                        bookingid_str=lst_to_str(bookingid)
                        delivery_boy_id_str=lst_to_str(delivery_boy_id)
                        booking_status_str=lst_to_str(booking_status)
                        time_at_str=lst_to_str(time_at)
                        branch_id_str=lst_to_str(branch_id)

                        jdict={
                                "booking_id":str(bookingid_str),
                                "delivery_boy_id":str(delivery_boy_id_str),
                                "booking_status":str(booking_status_str),
                                "booking_time":str(time_at_str),
                                "branch_id":str(branch_id_str),
                            }
                        return JsonResponse(jdict,safe=False)
                if reply_data == "ErrorCode#2":
                    query2="select bookingid,delivery_boy_id,booking_status,time_at,branch_id from vff.laundry_order_bookingtbl where  customerid='"+str(customer_id)+"' and delivery_boy_id='-1' and booking_status='NA'"
                    if query2 != "":
                        reply_data="ErrorCode#0"
                        mapVal = execute_query_and_get_result(query2)
                        if mapVal != None:
                            bookingid=mapVal["1"]
                            delivery_boy_id=mapVal["2"]
                            booking_status=mapVal["3"]
                            time_at=mapVal["4"]
                            branch_id=mapVal["5"]

                            bookingid_str=lst_to_str(bookingid)
                            delivery_boy_id_str=lst_to_str(delivery_boy_id)
                            booking_status_str=lst_to_str(booking_status)
                            time_at_str=lst_to_str(time_at)
                            branch_id_str=lst_to_str(branch_id)

                            jdict={
                                    "booking_id":str(bookingid_str),
                                    "delivery_boy_id":str(delivery_boy_id_str),
                                    "booking_status":str(booking_status_str),
                                    "booking_time":str(time_at_str),
                                    "branch_id":str(branch_id_str),
                                }
                            return JsonResponse(jdict,safe=False)
            
        except KeyError as e:
            print(f"{Fore.RED}KeyError: {e}{Style.RESET_ALL} - Key does not exist in the JSON")
            return JsonResponse('ErrorCode#8',safe=False)
        except json.JSONDecodeError as e:
            print(f"{Fore.RED}Failed to parse JSON: {e}{Style.RESET_ALL}")
            return JsonResponse('ErrorCode#8',safe=False)
        except Exception as ex:
            print(f"{Style.RESET_ALL}Error fetching data: {ex}{Style.RESET_ALL}")
            return JsonResponse('ErrorCode#8',safe=False)

    return JsonResponse(reply_data,safe=False)



@csrf_exempt
def send_notification_to_dashboard_without_delivery_boy(request,booking_id,senderid,mtitle,mbody,branch_id):
    if booking_id != "":
        title =mtitle
        body = mbody
        query="insert into vff.laundry_notificationtbl(title,body,reciever_id,sender_id,booking_id,branch_id) values ('"+str(title)+"','"+str(body)+"','-1','"+str(senderid)+"','"+str(booking_id)+"','"+str(branch_id)+"')"
        try:
            with connection.cursor() as cursor:
                cursor.execute(query)
                connection.commit()
        except Exception as e:
             print('Error Inserting Notification for send_notification_to_dashboard_without_delivery_boy')
             print(e)



@csrf_exempt
def send_notification_to_dashboard(request,booking_id,senderid,mtitle,mbody,mintent,mdata,branch_id,delivery_boy_id_str):
    if booking_id != "":
        title =mtitle
        body = mbody
        intent=mintent
        query="insert into vff.laundry_notificationtbl(title,body,intent,reciever_id,sender_id,booking_id,branch_id) values ('"+str(title)+"','"+str(body)+"','"+str(intent)+"','"+str(delivery_boy_id_str)+"','"+str(senderid)+"','"+str(booking_id)+"','"+str(branch_id)+"')"
        try:
            with connection.cursor() as cursor:
                cursor.execute(query)
                connection.commit()
        except Exception as e:
             print('Error Inserting Notification record for delivery boy')
             print(e)



@csrf_exempt
def send_notification_to_delivery_boy(request,booking_id,senderid,mtitle,mbody,mintent,mdata,branch_id):
    delivery_boy_id_str = ""
    global reply_data
    
    delivery_boy_id_str = ""
    try:
        query = "select usertbl.usrid,mobile_no,profile_img,device_token,delivery_boy_id,usrname,branchid from vff.laundry_delivery_boytbl,vff.usertbl where usertbl.usrid=laundry_delivery_boytbl.usrid and is_online='1' and status='Free' and branchid='"+str(branch_id)+"'"
        reply_data="ErrorCode#0"
        mapVal = execute_query_and_get_result(query)
        if mapVal != None:
            usrid = mapVal["1"]
            mobno=mapVal["2"]
            profile_img=mapVal["3"]
            device_token=mapVal["4"]
            delivery_boy_id=mapVal["5"]
            usrname=mapVal["6"]
            delivery_boy_branch_id=mapVal["7"]
            delivery_boy_id_str=delivery_boy_id[0]
            delivery_boy_branch_id_str=delivery_boy_branch_id[0]
            print(f'delivery_id::{delivery_boy_id_str}')
        elif reply_data == "ErrorCode#2":
            return JsonResponse(reply_data,safe=False)
        else:
            print('No Delivery Boy is Free or There are no Delivery Boys for this Branch ID'+str(booking_id))
            title='Pickup Request'
            body='Customer Pickup Request For Booking ID #'+str(booking_id)
            send_notification_to_dashboard_without_delivery_boy(request,booking_id,senderid,title,body,branch_id)
            return
    except Exception as e:
            print(e)
            reply_data="ErrorCode#8"
    if delivery_boy_id_str != "" or delivery_boy_id_str != None:
        title =mtitle
        body = mbody
        intent=mintent
        query="insert into vff.laundry_notificationtbl(title,body,intent,reciever_id,sender_id,booking_id,branch_id) values ('"+str(title)+"','"+str(body)+"','"+str(intent)+"','"+str(delivery_boy_id_str)+"','"+str(senderid)+"','"+str(booking_id)+"','"+str(delivery_boy_branch_id_str)+"')"
        try:
            with connection.cursor() as cursor:
                cursor.execute(query)
                connection.commit()
                #send notification to Delivery Boy
                title='Pickup Request'
                send_notification_to_dashboard(request,booking_id,senderid,title,body,intent,mdata,branch_id,delivery_boy_id_str)
                try:
                    print('Sending Notification to delivery boy')
                    print(f'DeviceToken_DeliveryBoy::{device_token[0]}')
                    data = mdata
                    sendFMCMsg(device_token[0],body,title,data)
                except Exception as e:
                    print('Error Sending Notification')
                    print(e)
        except Exception as e:
             print('Error Inserting Notification record for delivery boy')
             print(e)


'''
To Update order status at every stage of order
'''
@csrf_exempt
def update_order_status(request,order_id,status):
    query="insert into vff.laundry_order_historytbl(order_id,order_stages) values ('"+str(order_id)+"','"+str(status)+"')"
    try:
        with connection.cursor() as cursor:
            cursor.execute(query)
            connection.commit()
            print(f'Order Status Updated Successfully for OrderID:{order_id} Status:{status}')
    except Exception as e:
        print('Error Updating Order Status')
        print(e)



@csrf_exempt
def update_booking_status(request,booking_id,status):
    query="update vff.laundry_order_bookingtbl set booking_status='"+str(status)+"' where bookingid='"+str(booking_id)+"'"
    try:
        with connection.cursor() as cursor:
            cursor.execute(query)
            connection.commit()
        print(f'Booking Status Updated Successfully for BookingID:{booking_id} Status:{status}')
    except Exception as e:
        print('Error Updating Booking Status')
        print(e)


'''
Active Order Details for customer
'''
@csrf_exempt
def load_customer_active_order_details(request):
    global reply_data
    if request.method == "POST":
        try:
            
            jdict = json.loads(request.body)
            key = jdict['key']
            #booking_status = jdict['booking_status']#0 is for Fresh order,1 for Order Completed,2 for order Cancelled
            if key == 1:
                order_id = jdict['order_id']
                order_status = jdict['order_status']
                query = "select laundry_ordertbl.epoch,pickup_dt,clat,clng,delivery_boyid,name as delivery_boy_name,order_status,delivery as delivery_date,houseno,address,landmark,pincode,delivery_epoch,cancel_reason,feedback,laundry_ordertbl.customerid,mobile_no,usrname,payment_done,price from vff.usertbl,vff.laundry_delivery_boytbl,vff.laundry_customertbl,vff.laundry_ordertbl where laundry_customertbl.consmrid=laundry_ordertbl.customerid and usertbl.usrid=laundry_customertbl.usrid and laundry_delivery_boytbl.delivery_boy_id=laundry_ordertbl.delivery_boyid and order_completed='"+str(order_status)+"' and orderid='"+str(order_id)+"' order by orderid desc"

                if query != "":
                    reply_data="ErrorCode#0"
                    mapVal = execute_query_and_get_result(query)
                    if mapVal != None:
                        epoch=mapVal["1"]
                        pickup_dt=mapVal["2"]
                        clat=mapVal["3"]
                        clng=mapVal["4"]
                        delivery_boy_id=mapVal["5"]
                        delivery_boy_name=mapVal["6"]
                        order_status=mapVal["7"]
                        delivery_date=mapVal["8"]
                        houseno=mapVal["9"]
                        address=mapVal["10"]
                        landmark=mapVal["11"]
                        pincode=mapVal["12"]
                        delivery_epoch=mapVal["13"]
                        cancel_reason=mapVal["14"]
                        feedback=mapVal["15"]
                        customerid=mapVal["16"]
                        customer_mobile_no=mapVal["17"]
                        customer_name=mapVal["18"]
                        payment_done=mapVal["19"]
                        price=mapVal["20"]



                        #fetch mobile number of delivery boy
                        query2="select mobile_no,profile_img,usrname from vff.laundry_delivery_boytbl,vff.usertbl where laundry_delivery_boytbl.usrid=usertbl.usrid and delivery_boy_id='"+str(delivery_boy_id[0])+"'"
                        if query2 != "":
                            reply_data="ErrorCode#0"
                            mapVal = execute_query_and_get_result(query2)
                            if mapVal != None:
                                mobno = mapVal["1"]
                                profile_img = mapVal["2"]

                            jdict={
                                    "epoch":str(epoch[0]),
                                    "pickup_dt":str(pickup_dt[0]),
                                    "clat":str(clat[0]),
                                    "clng":str(clng[0]),
                                    "delivery_boy_id":str(delivery_boy_id[0]),
                                    "delivery_boy_name":str(delivery_boy_name[0]),
                                    "order_status":str(order_status[0]),
                                    "delvry_boy_mobno":str(mobno[0]),
                                    "delivery_dt":str(delivery_date[0]),
                                    "houseno":str(houseno[0]),
                                    "address":str(address[0]),
                                    "landmark":str(landmark[0]),
                                    "pincode":str(pincode[0]),
                                    "deliveryEpoch":str(delivery_epoch[0]),
                                    "profileImg":str(profile_img[0]),
                                    "cancel_reason":str(cancel_reason[0]),
                                    "feedback":str(feedback[0]),
                                    "customer_id":str(customerid[0]),
                                    "customer_mobno":str(customer_mobile_no[0]),
                                    "customer_name":str(customer_name[0]),
                                    "payment_done":str(payment_done[0]),
                                    "total_price":str(price[0]),
                            }
                            return JsonResponse(jdict,safe=False)


            else:
                booking_id = jdict['booking_id']
                query = "select customerid,laundry_order_bookingtbl.delivery_boy_id,usertbl.address,usertbl.city,usertbl.pincode,usertbl.landmark,clat,clng,booking_status,time_at,usrname,mobile_no from vff.usertbl,vff.laundry_customertbl,vff.laundry_order_bookingtbl where laundry_customertbl.consmrid=laundry_order_bookingtbl.customerid and usertbl.usrid=laundry_customertbl.usrid and delivery_boy_id!='-1' and bookingid='"+str(booking_id)+"'"
                if query != "":
                    reply_data="ErrorCode#0"
                    mapVal = execute_query_and_get_result(query)
                    if mapVal != None:
                        customerid=mapVal["1"]
                        delivery_boy_id=mapVal["2"]
                        address=mapVal["3"]
                        city=mapVal["4"]
                        pincode=mapVal["5"]
                        landmark=mapVal["6"]
                        clat=mapVal["7"]
                        clng=mapVal["8"]
                        booking_status=mapVal["9"]
                        time_at=mapVal["10"]
                        customer_name=mapVal["11"]
                        customer_mobile_no=mapVal["12"]


                        #fetch mobile number of delivery boy
                        query2="select mobile_no,profile_img,usrname from vff.laundry_delivery_boytbl,vff.usertbl where laundry_delivery_boytbl.usrid=usertbl.usrid and delivery_boy_id='"+str(delivery_boy_id[0])+"'"
                        if query2 != "":
                            reply_data="ErrorCode#0"
                            mapVal = execute_query_and_get_result(query2)
                            if mapVal != None:
                                mobno = mapVal["1"]
                                profile_img = mapVal["2"]
                                delivery_boy_name = mapVal["3"]

                            jdict={
                                    "customerid":str(customerid[0]),
                                    "delivery_boy_id":str(delivery_boy_id[0]),
                                    "clat":str(clat[0]),
                                    "clng":str(clng[0]),
                                    "delivery_boy_name":str(delivery_boy_name[0]),
                                    "booking_status":str(booking_status[0]),
                                    "time_at":str(time_at[0]),
                                    "delvry_boy_mobno":str(mobno[0]),
                                    "address":str(address[0]),
                                    "city":str(city[0]),
                                    "landmark":str(landmark[0]),
                                    "pincode":str(pincode[0]),
                                    "profileImg":str(profile_img[0]),
                                    "delivery_boy_mobno":str(mobno[0]),
                                    "customer_name":str(customer_name[0]),
                                    "customer_mobile_no":str(customer_mobile_no[0]),
                            }
                            return JsonResponse(jdict,safe=False)
            
        except KeyError as e:
            print(f"{Fore.RED}KeyError: {e}{Style.RESET_ALL} - Key does not exist in the JSON")
            return JsonResponse('ErrorCode#8',safe=False)
        except json.JSONDecodeError as e:
            print(f"{Fore.RED}Failed to parse JSON: {e}{Style.RESET_ALL}")
            return JsonResponse('ErrorCode#8',safe=False)
        except Exception as ex:
            print(f"{Style.RESET_ALL}Error fetching data: {ex}{Style.RESET_ALL}")
            return JsonResponse('ErrorCode#8',safe=False)

    return JsonResponse(reply_data,safe=False)



@csrf_exempt
def load_selected_order_items_order_detail(request):
    global reply_data
    if request.method == "POST":
        try:
            
            jdict = json.loads(request.body)
            order_id = jdict['order_id']

            query="select cat_name,cat_img,sub_cat_name,sub_cat_img,categoryid,subcategoryid,booking_type,dt,time,item_cost,item_quantity,type,section_type from vff.laundry_active_orders_tbl where order_id='"+str(order_id)+"'"
            if query != "":
                reply_data="ErrorCode#0"
                mapVal = execute_query_and_get_result(query)
                if mapVal != None:
                    category_name=mapVal["1"]
                    cat_img=mapVal["2"]
                    sub_cat_name=mapVal["3"]
                    sub_cat_img=mapVal["4"]
                    cat_id=mapVal["5"]
                    sub_cat_id=mapVal["6"]
                    order_type=mapVal["7"]
                    dt=mapVal["8"]
                    time=mapVal["9"]
                    item_cost=mapVal["10"]
                    item_quantity=mapVal["11"]
                    type_of=mapVal["12"]
                    section_type=mapVal["13"]


                    category_name_str=lst_to_str(category_name)
                    cat_img_str=lst_to_str(cat_img)
                    sub_cat_name_str=lst_to_str(sub_cat_name)
                    sub_cat_img_str=lst_to_str(sub_cat_img)
                    cat_id_str=lst_to_str(cat_id)
                    sub_cat_id_str=lst_to_str(sub_cat_id)
                    order_type_str=lst_to_str(order_type)
                    dt_str=lst_to_str(dt)
                    time_str=lst_to_str(time)
                    item_cost_str=lst_to_str(item_cost)
                    item_quantity_str=lst_to_str(item_quantity)
                    type_of_str=lst_to_str(type_of)
                    section_type_str=lst_to_str(section_type)


                    query2 = "select sum(item_cost) as total_price,sum(item_quantity) as total_quantity from vff.laundry_ordertbl,vff.laundry_cart_items where laundry_cart_items.booking_id=laundry_ordertbl.booking_id and laundry_ordertbl.orderid='"+str(order_id)+"'"
                    if query2 != "":
                        reply_data="ErrorCode#0"
                        mapVal = execute_query_and_get_result(query2)
                        if mapVal != None:

                            total_quantity_extra=mapVal["2"]
                            total_price_extra=mapVal["1"]

                            total_quantity_extra_str=lst_to_str(total_quantity_extra)
                            total_price_extra_str=lst_to_str(total_price_extra)

                    jdict={
                            "category_name":str(category_name_str),
                            "cat_img":str(cat_img_str),
                            "sub_cat_name":str(sub_cat_name_str),
                            "sub_cat_img":str(sub_cat_img_str),
                            "cat_id":str(cat_id_str),
                            "sub_cat_id":str(sub_cat_id_str),
                            "order_type":str(order_type_str),
                            "dt":str(dt_str),
                            "time":str(time_str),
                            "item_cost":str(item_cost_str),
                            "item_quantity":str(item_quantity_str),
                            "type_of":str(type_of_str),
                            "total_items_count":str(total_quantity_extra_str),
                            "total_item_price":str(total_price_extra_str),
                            "section_type":str(section_type_str),
                            }
                    return JsonResponse(jdict,safe=False)
             
        except KeyError as e:
            print(f"{Fore.RED}KeyError: {e}{Style.RESET_ALL} - Key does not exist in the JSON")
            return JsonResponse('ErrorCode#8',safe=False)
        except json.JSONDecodeError as e:
            print(f"{Fore.RED}Failed to parse JSON: {e}{Style.RESET_ALL}")
            return JsonResponse('ErrorCode#8',safe=False)
        except Exception as ex:
            print(f"{Style.RESET_ALL}Error fetching data: {ex}{Style.RESET_ALL}")
            return JsonResponse('ErrorCode#8',safe=False)

    return JsonResponse('ErrorCode#8',safe=False)



@csrf_exempt
def load_category_wise_details(request):
    global reply_data
    if request.method == "POST":
        try:
            
            jdict = json.loads(request.body)
            cat_id = jdict['cat_id']

            query="select category_name,regular_price,regular_price_type,express_price_type,express_price,offer_price,offer_price_type,cat_img from vff.laundry_categorytbl where catid='"+str(cat_id)+"'"
            if query != "":
                reply_data="ErrorCode#0"
                mapVal = execute_query_and_get_result(query)
                if mapVal != None:
                    categoryname=mapVal["1"]
                    reg_price=mapVal["2"]
                    reg_type=mapVal["3"]
                    exp_type=mapVal["4"]
                    exp_price=mapVal["5"]
                    offer_price=mapVal["6"]
                    offer_type=mapVal["7"]
                    cat_img=mapVal["8"]


                    categoryname_str=lst_to_str(categoryname)
                    reg_price_str=lst_to_str(reg_price)
                    reg_type_str=lst_to_str(reg_type)
                    exp_price_str=lst_to_str(exp_price)
                    exp_type_str=lst_to_str(exp_type)
                    offer_price_str=lst_to_str(offer_price)
                    offer_type_str=lst_to_str(offer_type)
                    cat_img_str=lst_to_str(cat_img)


                    jdict={
                            "categoryname":str(categoryname_str),
                            "regular_price":str(reg_price_str),
                            "regular_type":str(reg_type_str),
                            "express_price":str(exp_price_str),
                            "express_type":str(exp_type_str),
                            "offer_price":str(offer_price_str),
                            "offer_type":str(offer_type_str),
                            "cat_img":str(cat_img_str),
                            }
                    return JsonResponse(jdict,safe=False)
            
        except KeyError as e:
            print(f"{Fore.RED}KeyError: {e}{Style.RESET_ALL} - Key does not exist in the JSON")
            return JsonResponse('ErrorCode#8',safe=False)
        except json.JSONDecodeError as e:
            print(f"{Fore.RED}Failed to parse JSON: {e}{Style.RESET_ALL}")
            return JsonResponse('ErrorCode#8',safe=False)
        except Exception as ex:
            print(f"{Style.RESET_ALL}Error fetching data: {ex}{Style.RESET_ALL}")
            return JsonResponse('ErrorCode#8',safe=False)

    return JsonResponse(reply_data,safe=False)



@csrf_exempt
def load_sub_category_wise_details(request):
    global reply_data
    if request.method == "POST":
        try:
            
            jdict = json.loads(request.body)
            cat_id = jdict['cat_id']

            query="select sub_cat_name,sub_cat_img,cost,type,section_type,subcatid from vff.laundry_sub_categorytbl where catid='"+str(cat_id)+"'"
            if query != "":
                reply_data="ErrorCode#0"
                mapVal = execute_query_and_get_result(query)
                if mapVal != None:
                    sub_categoryname=mapVal["1"]
                    sub_cat_img=mapVal["2"]
                    cost=mapVal["3"]
                    type_of=mapVal["4"]
                    section_type=mapVal["5"]
                    subcatid=mapVal["6"]

                    query2 = "select sectionid,section_name from vff.laundry_sub_category_sectiontbl"
                    if query2 != None:
                        reply_data="ErrorCode#0"
                        mapVal = execute_query_and_get_result(query2)
                        if mapVal != None:
                            sec_id=mapVal["1"]
                            sec_name=mapVal["2"]

                            sec_id_str = lst_to_str(sec_id)
                            sec_name_str = lst_to_str(sec_name)


                            sub_categoryname_str=lst_to_str(sub_categoryname)
                            sub_cat_img_str=lst_to_str(sub_cat_img)
                            cost_str=lst_to_str(cost)
                            type_of_str=lst_to_str(type_of)
                            subcatid_str=lst_to_str(subcatid)


                    jdict={
                            "sub_categoryname":str(sub_categoryname_str),
                            "subcat_img":str(sub_cat_img_str),
                            "cost":str(cost_str),
                            "type_of":str(type_of_str),
                            "section_type":str(sec_name_str),
                            "sub_catid":str(subcatid_str),
                            }
                    return JsonResponse(jdict,safe=False)

        except KeyError as e:
            print(f"{Fore.RED}KeyError: {e}{Style.RESET_ALL} - Key does not exist in the JSON")
            return JsonResponse('ErrorCode#8',safe=False)
        except json.JSONDecodeError as e:
            print(f"{Fore.RED}Failed to parse JSON: {e}{Style.RESET_ALL}")
            return JsonResponse('ErrorCode#8',safe=False)
        except Exception as ex:
            print(f"{Style.RESET_ALL}Error fetching data: {ex}{Style.RESET_ALL}")
            return JsonResponse('ErrorCode#8',safe=False)

    return JsonResponse(reply_data,safe=False)



@csrf_exempt
def load_sub_category_section_wise_details(request):
    global reply_data
    if request.method == "POST":
        try:
            jdict = json.loads(request.body)
            section_type = jdict['section_type']

            query="select sub_cat_name,sub_cat_img,cost,type,subcatid from vff.laundry_sub_categorytbl where section_type='"+str(section_type)+"'"
            if query != "":
                reply_data="ErrorCode#0"
                mapVal = execute_query_and_get_result(query)
                if mapVal != None:
                    sub_categoryname=mapVal["1"]
                    sub_cat_img=mapVal["2"]
                    cost=mapVal["3"]
                    type_of=mapVal["4"]
                    subcatid=mapVal["5"]


                    sub_categoryname_str=lst_to_str(sub_categoryname)
                    sub_cat_img_str=lst_to_str(sub_cat_img)
                    cost_str=lst_to_str(cost)
                    type_of_str=lst_to_str(type_of)
                    subcatid_str=lst_to_str(subcatid)


                    jdict={
                            "sub_categoryname":str(sub_categoryname_str),
                            "subcat_img":str(sub_cat_img_str),
                            "cost":str(cost_str),
                            "type_of":str(type_of_str),
                            "sub_catid":str(subcatid_str),
                            }
                    return JsonResponse(jdict,safe=False)
        except KeyError as e:
            print(f"{Fore.RED}KeyError: {e}{Style.RESET_ALL} - Key does not exist in the JSON")
            return JsonResponse('ErrorCode#8',safe=False)
        except json.JSONDecodeError as e:
            print(f"{Fore.RED}Failed to parse JSON: {e}{Style.RESET_ALL}")
            return JsonResponse('ErrorCode#8',safe=False)
        except Exception as ex:
            print(f"{Style.RESET_ALL}Error fetching data: {ex}{Style.RESET_ALL}")
            return JsonResponse('ErrorCode#8',safe=False)

    return JsonResponse('ErrorCode#8',safe=False)



@csrf_exempt
def add_laundry_items_to_cart(request):
    global reply_data
    if request.method == "POST":
        try:
            jdict=json.loads(request.body)
            cat_id = jdict['cat_id']
            customer_id = jdict['customer_id']
            booking_id = jdict['booking_id']
            booking_type = jdict['booking_type']
            cat_img = jdict['cat_img']
            cat_name = jdict['cat_name']
            key = jdict['key']
            if key == 1:

                all_data = jdict['all_items']
                try:
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
                        query = "insert into vff.laundry_cart_items(catid,subcatid,customer_id,booking_id,booking_type,item_cost,item_quantity,type,cat_img,cat_name,sub_cat_name,sub_cat_img,actual_cost,section_type) values ('"+str(cat_id)+"','"+str(sub_cat_id)+"','"+str(customer_id)+"','"+str(booking_id)+"','"+str(booking_type)+"','"+str(cost)+"','"+str(item_quantity)+"','"+str(type_of)+"','"+str(cat_img)+"','"+str(cat_name)+"','"+str(sub_cat_name)+"','"+str(sub_cat_img)+"','"+str(actual_cost)+"','"+str(section_type)+"')"

                        with connection.cursor() as cursor:
                            cursor.execute(query)
                            connection.commit()
                            reply_data="ErrorCode#0"
                except Exception as e:
                    print(e)
                    reply_data ="ErrorCode#8"
            else:
                sub_cat_name = jdict['sub_cat_name']
                item_quantity = jdict['item_quantity']
                actual_cost = jdict['actual_cost']
                cost = jdict['cost']
                type_of = jdict['type_of']
                sub_cat_id = jdict['sub_cat_id']
                sub_cat_img = jdict['sub_cat_img']
                section_type = jdict['section_type']
                query2 = "insert into vff.laundry_cart_items(catid,subcatid,customer_id,booking_id,booking_type,item_cost,item_quantity,type,cat_img,cat_name,sub_cat_name,sub_cat_img,actual_cost,section_type) values ('"+str(cat_id)+"','"+str(sub_cat_id)+"','"+str(customer_id)+"','"+str(booking_id)+"','"+str(booking_type)+"','"+str(cost)+"','"+str(item_quantity)+"','"+str(type_of)+"','"+str(cat_img)+"','"+str(cat_name)+"','"+str(sub_cat_name)+"','"+str(sub_cat_img)+"','"+str(actual_cost)+"','"+str(section_type)+"')"
                print(f'Insert Query::{query2}')
                try:
                    with connection.cursor() as cursor:
                        cursor.execute(query2)
                        connection.commit()
                        reply_data="ErrorCode#0"
                except Exception as e:
                    print(e)
                    reply_data ="ErrorCode#8"
        except KeyError as e:
            print(f"{Fore.RED}KeyError: {e}{Style.RESET_ALL} - Key does not exist in the JSON")
            return JsonResponse('ErrorCode#8',safe=False)
        except json.JSONDecodeError as e:
            print(f"{Fore.RED}Failed to parse JSON: {e}{Style.RESET_ALL}")
            return JsonResponse('ErrorCode#8',safe=False)
        except Exception as ex:
            print(f"{Style.RESET_ALL}Error fetching data: {ex}{Style.RESET_ALL}")
            return JsonResponse('ErrorCode#8',safe=False)

    return JsonResponse(reply_data,safe=False)



@csrf_exempt
def delete_laundry_cart_item(request):
    global reply_data
    if request.method == "POST":
        try:
            jdict=json.loads(request.body)
            item_id = jdict['item_id']

            query = "delete from vff.laundry_cart_items where itemid='"+str(item_id)+"'"
            try:
                with connection.cursor() as cursor:
                    cursor.execute(query)
                    connection.commit()
                    reply_data="ErrorCode#0"
            except Exception as e:
                print(e)
                reply_data ="ErrorCode#8"
        except KeyError as e:
            print(f"{Fore.RED}KeyError: {e}{Style.RESET_ALL} - Key does not exist in the JSON")
            return JsonResponse('ErrorCode#8',safe=False)
        except json.JSONDecodeError as e:
            print(f"{Fore.RED}Failed to parse JSON: {e}{Style.RESET_ALL}")
            return JsonResponse('ErrorCode#8',safe=False)
        except Exception as ex:
            print(f"{Style.RESET_ALL}Error fetching data: {ex}{Style.RESET_ALL}")
            return JsonResponse('ErrorCode#8',safe=False)

    return JsonResponse(reply_data,safe=False)



@csrf_exempt
def load_cart_items_selected(request):
    global reply_data
    if request.method == "POST":
        try:
            
            jdict = json.loads(request.body)
            customer_id = jdict['customer_id']
            booking_id = jdict['booking_id']           
            query="select itemid,catid,subcatid,booking_id,dt,time,booking_type,item_cost,item_quantity,type,cat_img,cat_name,sub_cat_name,sub_cat_img,actual_cost,section_type from vff.laundry_cart_items where customer_id='"+str(customer_id)+"' and booking_id='"+str(booking_id)+"'"
            if query != "":
                reply_data="ErrorCode#0"
                mapVal = execute_query_and_get_result(query)
                if mapVal != None:
                    itemid=mapVal["1"]
                    catid=mapVal["2"]
                    subcatid=mapVal["3"]
                    order_id=mapVal["4"]
                    dt=mapVal["5"]
                    time=mapVal["6"]
                    order_type=mapVal["7"]
                    item_cost=mapVal["8"]
                    item_quantity=mapVal["9"]
                    type_of=mapVal["10"]
                    category_img=mapVal["11"]
                    category_name=mapVal["12"]
                    sub_cat_name=mapVal["13"]
                    sub_cat_img=mapVal["14"]
                    actual_cost=mapVal["15"]
                    section_type=mapVal["16"]                      
                    itemid_str=lst_to_str(itemid)
                    catid_str=lst_to_str(catid)
                    subcatid_str=lst_to_str(subcatid)
                    order_id_str=lst_to_str(order_id)
                    date_str=lst_to_str(dt)
                    time_str=lst_to_str(time)
                    order_type_str=lst_to_str(order_type)
                    item_cost_str=lst_to_str(item_cost)
                    item_quantity_str=lst_to_str(item_quantity)
                    type_of_str=lst_to_str(type_of)
                    category_img_str=lst_to_str(category_img)
                    category_name_str=lst_to_str(category_name)
                    sub_cat_name_str=lst_to_str(sub_cat_name)
                    sub_cat_img_str=lst_to_str(sub_cat_img)
                    actual_cost_str=lst_to_str(actual_cost)
                    section_type_str=lst_to_str(section_type)          
                    jdict={
                            "itemid":str(itemid_str),
                            "catid":str(catid_str),
                            "subcatid":str(subcatid_str),
                            "order_id":str(order_id_str),
                            "date":str(date_str),
                            "time":str(time_str),
                            "order_type":str(order_type_str),
                            "item_cost":str(item_cost_str),
                            "item_quantity":str(item_quantity_str),
                            "type_of":str(type_of_str),
                            "category_img":str(category_img_str),
                            "category_name":str(category_name_str),
                            "sub_cat_name":str(sub_cat_name_str),
                            "sub_cat_img":str(sub_cat_img_str),
                            "actual_cost":str(actual_cost_str),
                            "section_type":str(section_type_str),          
                            }
                    return JsonResponse(jdict,safe=False)
            
        except KeyError as e:
            print(f"{Fore.RED}KeyError: {e}{Style.RESET_ALL} - Key does not exist in the JSON")
            return JsonResponse('ErrorCode#8',safe=False)
        except json.JSONDecodeError as e:
            print(f"{Fore.RED}Failed to parse JSON: {e}{Style.RESET_ALL}")
            return JsonResponse('ErrorCode#8',safe=False)
        except Exception as ex:
            print(f"{Style.RESET_ALL}Error fetching data: {ex}{Style.RESET_ALL}")
            return JsonResponse('ErrorCode#8',safe=False)

    return JsonResponse(reply_data,safe=False)



@csrf_exempt
def load_extra_items_details(request):
    global reply_data
    if request.method == "POST":
        try:
            
            jdict = json.loads(request.body)
            booking_id = jdict['booking_id']

            query="select extra_item_id,extra_item_name,price from vff.laundry_extra_items_tbl"
            if query != "":
                reply_data="ErrorCode#0"
                mapVal = execute_query_and_get_result(query)
                if mapVal != None:
                    itemid=mapVal["1"]
                    item_name=mapVal["2"]
                    price=mapVal["3"]


                    itemid_str=lst_to_str(itemid)
                    item_name_str=lst_to_str(item_name)
                    price_str=lst_to_str(price)


                    query2="select sum(item_cost) as total_price,sum(item_quantity) as total_quantity from vff.laundry_cart_items where booking_id='"+str(booking_id)+"'"
                    if query2 != "":
                        reply_data="ErrorCode#0"
                        mapVal = execute_query_and_get_result(query2)
                    if mapVal != None:
                        total_price=mapVal["1"]
                        total_quantity=mapVal["2"]


                        total_price_str=lst_to_str(total_price)
                        total_quantity_str=lst_to_str(total_quantity)

                        #To get delivery charges for delivery
                        query3="select dcharge_id,price,range from vff.laundry_delivery_chargetbl"
                        if query3 != "":
                            reply_data="ErrorCode#0"
                            mapVal = execute_query_and_get_result(query3)
                        if mapVal != None:
                            dcharge_id = mapVal["1"]
                            price_delivery = mapVal["2"]
                            range_delivery = mapVal["3"]

                            dcharge_id_str=lst_to_str(dcharge_id)
                            price_delivery_str=lst_to_str(price_delivery)
                            range_delivery_str=lst_to_str(range_delivery)

                    jdict={
                            "itemid":str(itemid_str),
                            "item_name":str(item_name_str),
                            "price":str(price_str),
                            "total_price":str(total_price_str),
                            "total_quantity":str(total_quantity_str),
                            "dcharge_id":str(dcharge_id_str),
                            "price_delivery":str(price_delivery_str),
                            "range_delivery":str(range_delivery_str),
                            }
                    return JsonResponse(jdict,safe=False)
    
            
        except KeyError as e:
            print(f"{Fore.RED}KeyError: {e}{Style.RESET_ALL} - Key does not exist in the JSON")
            return JsonResponse('ErrorCode#8',safe=False)
        except json.JSONDecodeError as e:
            print(f"{Fore.RED}Failed to parse JSON: {e}{Style.RESET_ALL}")
            return JsonResponse('ErrorCode#8',safe=False)
        except Exception as ex:
            print(f"{Style.RESET_ALL}Error fetching data: {ex}{Style.RESET_ALL}")
            return JsonResponse('ErrorCode#8',safe=False)

    return JsonResponse(reply_data,safe=False)


@csrf_exempt
def place_order_laundry(request):
    global reply_data
    if request.method == "POST":
        try:
            
            jdict=json.loads(request.body)
            booking_id = jdict['booking_id']
            customer_id = jdict['customer_id']
            total_price = jdict['total_price']
            total_items = jdict['total_items']
            order_status = jdict['order_status']
            razor_pay_id = jdict['razor_pay_id']
            payment_status = jdict['payment_status']
            payment_type = jdict['payment_type']
            delivery_charges = jdict['delivery_charges']
            gstamount = jdict['gstamount']
            extra_item_dict = jdict['extra_items']
            additional_instruction = jdict['additional_instruction']

            delivery_boy_id = jdict['delivery_boy_id']
            clat = jdict['clat']
            clng = jdict['clng']
            branch_id = jdict['branch_id']


            #Insert Record into Order Table First to Generate Order ID
            query_order = "insert into vff.laundry_ordertbl(customerid,delivery_boyid,quantity,price,clat,clng,order_status,additional_instruction,booking_id,branch_id,delivery_price,gstamount) values ('"+str(customer_id)+"','"+str(delivery_boy_id)+"','"+str(total_items)+"','"+str(total_price)+"','"+str(clat)+"','"+str(clng)+"','"+str(order_status)+"','"+str(additional_instruction)+"','"+str(booking_id)+"','"+str(branch_id)+"','"+str(delivery_charges)+"','"+str(gstamount)+"') returning orderid"
            try:

                    try:
                        with connection.cursor() as cursor:
                            cursor.execute(query_order)
                            connection.commit()
                            data = cursor.fetchall()
                        if len(data) !=0:
                            order_id=str(data[0][0])
                            print('----------Returning Order ID-----> '+str(order_id))
                            #Insert record in payment table with razorpay_payment_id
                            query = "insert into vff.laundry_payment_tbl(order_id,razor_pay_payment_id,status,payment_type,branch_id) values ('"+str(order_id)+"','"+str(razor_pay_id)+"','"+str(payment_status)+"','"+str(payment_type)+"','"+str(branch_id)+"')"
                            print(f'insert payment::{query}')
                            try:
                                with connection.cursor() as cursor:
                                    cursor.execute(query)
                                    connection.commit()
                                #obj.reply_data="ErrorCode#0"
                                #Adding all cart items into active order table 
                                query2="insert into vff.laundry_active_orders_tbl(order_id,booking_id,categoryid,subcategoryid,booking_type,item_cost,item_quantity,type,cat_img,cat_name,sub_cat_name,sub_cat_img,actual_cost,section_type) select "+str(order_id)+" as order_id,booking_id,catid,subcatid,booking_type,item_cost,item_quantity,type,cat_img,cat_name,sub_cat_name,sub_cat_img,actual_cost,section_type from vff.laundry_cart_items where customer_id='"+str(customer_id)+"' and booking_id='"+str(booking_id)+"'"
                                print(f'query2::{query2}')
                                try:
                                    with connection.cursor() as cursor:
                                        cursor.execute(query2)
                                        connection.commit()
                                 #   obj.reply_data="ErrorCode#0"
                                except Exception as e:
                                    print(e)
                                    reply_data = "ErrorCode#8"

                                #Updating Order ID in Order Assignment Table
                                query_assignment_update="update vff.laundry_order_assignmenttbl set order_id='"+str(order_id)+"' where booking_id='"+str(booking_id)+"'"
                                try:
                                    with connection.cursor() as cursor:
                                        cursor.execute(query_assignment_update)
                                        connection.commit()
                                 #   obj.reply_data="ErrorCode#0"
                                except Exception as e:
                                    print(e)
                                    reply_data = "ErrorCode#8"

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
                                        with connection.cursor() as cursor:
                                            cursor.execute(query3)
                                            connection.commit()
                                  #  obj.reply_data="ErrorCode#0"
                                except Exception as e:
                                    print(e)
                                    reply_data = "ErrorCode#8"



                                #Insert a record in order history table
                                update_order_status(request,order_id,order_status)

                                reply_data="ErrorCode#0"
                            except Exception as e:
                                print(e)
                                reply_data ="ErrorCode#8"
                            reply_data="ErrorCode#0"
                    except Exception as e:
                        print(e)
                        reply_data = "ErrorCode#8"
            except Exception as e :
                print(e)
                reply_data = "ErrorCode#8"
            
        except KeyError as e:
            print(f"{Fore.RED}KeyError: {e}{Style.RESET_ALL} - Key does not exist in the JSON")
            return JsonResponse('ErrorCode#8',safe=False)
        except json.JSONDecodeError as e:
            print(f"{Fore.RED}Failed to parse JSON: {e}{Style.RESET_ALL}")
            return JsonResponse('ErrorCode#8',safe=False)
        except Exception as ex:
            print(f"{Style.RESET_ALL}Error fetching data: {ex}{Style.RESET_ALL}")
            return JsonResponse('ErrorCode#8',safe=False)

    return JsonResponse(reply_data,safe=False)



@csrf_exempt
def cancel_laundry_order(request):
    global reply_data
    if request.method == "POST":
        try:
            jdict=json.loads(request.body)
            booking_id = jdict['booking_id']
            customer_id = jdict['customer_id']
            delivery_boy_id = jdict['delivery_boy_id']
            reason = jdict['reason']
            #cancel_reason,cancelled_at,booking_status
            query = "update vff.laundry_order_bookingtbl set booking_status='Cancelled',cancel_reason='"+str(reason)+"' where bookingid='"+str(booking_id)+"' and customerid='"+str(customer_id)+"'"
            try:
                with connection.cursor() as cursor:
                    cursor.execute(query)
                    connection.commit()
                    reply_data="ErrorCode#0"
                    status = 'Cancelled'
                    query3="update vff.laundry_order_assignmenttbl set type_of_order='Cancelled' where booking_id='"+str(booking_id)+"'"
                    try:
                        with connection.cursor() as cursor:
                            cursor.execute(query3)
                            connection.commit()
                    except Exception as e:
                        print(e)
                        reply_data ="ErrorCode#8"
                    query2 = "update vff.laundry_delivery_boytbl set status='Free' where delivery_boy_id='"+str(delivery_boy_id)+"'"
                    try:
                        with connection.cursor() as cursor:
                            cursor.execute(query2)
                            connection.commit()
                        #TODO:Need to send notification to delivery boy that the order is cancelled
                        title ="Booking Cancelled"
                        body = "Booking for Pickup Request was cancelled by Customer for Booking ID:#"+str(booking_id)+". You are free to accept New Orders Thank You"
                        intent="MainRoute"
                        mdata = {
                                 'intent':'MainRoute',
                                }
                        send_notification_to_assigned_delivery_boy_for_booking(request,customer_id,title,body,intent,booking_id,mdata)
                        reply_data="ErrorCode#0"
                    except Exception as e:
                        print(e)
                        reply_data ="ErrorCode#8"
            except Exception as e:
                print(e)
                reply_data ="ErrorCode#8"
        except KeyError as e:
            print(f"{Fore.RED}KeyError: {e}{Style.RESET_ALL} - Key does not exist in the JSON")
            return JsonResponse('ErrorCode#8',safe=False)
        except json.JSONDecodeError as e:
            print(f"{Fore.RED}Failed to parse JSON: {e}{Style.RESET_ALL}")
            return JsonResponse('ErrorCode#8',safe=False)
        except Exception as ex:
            print(f"{Style.RESET_ALL}Error fetching data: {ex}{Style.RESET_ALL}")
            return JsonResponse('ErrorCode#8',safe=False)

    return JsonResponse(reply_data,safe=False)



@csrf_exempt
def feedback_laundry_order(request):
    global reply_data
    if request.method == "POST":
        try:
            jdict=json.loads(request.body)
            order_id = jdict['order_id']
            customer_id = jdict['customer_id']
            feedback = jdict['feedback']

            query = "update vff.laundry_ordertbl set feedback='"+str(feedback)+"' where orderid='"+str(order_id)+"' and customerid='"+str(customer_id)+"'"
            try:
                with connection.cursor() as cursor:
                    cursor.execute(query)
                    connection.commit()
                    reply_data="ErrorCode#0"
            except Exception as e:
                print(e)
                reply_data ="ErrorCode#8"
        except KeyError as e:
            print(f"{Fore.RED}KeyError: {e}{Style.RESET_ALL} - Key does not exist in the JSON")
            return JsonResponse('ErrorCode#8',safe=False)
        except json.JSONDecodeError as e:
            print(f"{Fore.RED}Failed to parse JSON: {e}{Style.RESET_ALL}")
            return JsonResponse('ErrorCode#8',safe=False)
        except Exception as ex:
            print(f"{Style.RESET_ALL}Error fetching data: {ex}{Style.RESET_ALL}")
            return JsonResponse('ErrorCode#8',safe=False)

    return JsonResponse(reply_data,safe=False)



@csrf_exempt
def mark_delivery_boy_as_online(request):
    global reply_data
    if request.method == "POST":
        try:
            jdict=json.loads(request.body)
            delivery_boy_id = jdict['delivery_boy_id']
            set_free= jdict['set_free']
            filterc = ""
            if set_free=="Free":
                filterc=",status='Free'"

            query = "update vff.laundry_delivery_boytbl set is_online='1'"+str(filterc)+" where delivery_boy_id='"+str(delivery_boy_id)+"'"
            try:
                with connection.cursor() as cursor:
                    cursor.execute(query)
                    connection.commit()
                #obj.reply_data="ErrorCode#0"
                get_query = "select status from vff.laundry_delivery_boytbl where delivery_boy_id='"+str(delivery_boy_id)+"'"
                print(f'get_query:{get_query}')
                if get_query != None:
                     mapVal = execute_query_and_get_result(get_query)
                     if mapVal != None:
                    
                         status=mapVal["1"]

                         status_str = lst_to_str(status)
                         jdict = {
                                'status':status_str
                                }
                         return JsonResponse(jdict,safe=False)

            except Exception as e:
                print(e)
                reply_data ="ErrorCode#8"
        except KeyError as e:
            print(f"{Fore.RED}KeyError: {e}{Style.RESET_ALL} - Key does not exist in the JSON")
            return JsonResponse('ErrorCode#8',safe=False)
        except json.JSONDecodeError as e:
            print(f"{Fore.RED}Failed to parse JSON: {e}{Style.RESET_ALL}")
            return JsonResponse('ErrorCode#8',safe=False)
        except Exception as ex:
            print(f"{Style.RESET_ALL}Error fetching data: {ex}{Style.RESET_ALL}")
            return JsonResponse('ErrorCode#8',safe=False)

    return JsonResponse(reply_data,safe=False)



@csrf_exempt
def load_all_orders_tab_details(request):
    global reply_data
    if request.method == "POST":
        try:
            jdict = json.loads(request.body)
            customer_id = jdict['customer_id']
            order_status = jdict['order_status']
            query = "select orderid,delivery_boyid,quantity,price,pickup_dt,delivery,clat,clng,order_status,delivery_epoch,laundry_ordertbl.epoch,cancel_reason,houseno,address from vff.usertbl,vff.laundry_customertbl,vff.laundry_ordertbl where usertbl.usrid=laundry_customertbl.usrid and laundry_customertbl.consmrid=laundry_ordertbl.customerid and customerid='"+str(customer_id)+"' and order_completed='"+str(order_status)+"'  order by orderid desc"
            if query != "":
                reply_data="ErrorCode#0"
                mapVal = execute_query_and_get_result(query)
                if mapVal != None:
                    orderid=mapVal["1"]
                    delivery_boyid=mapVal["2"]
                    quantity=mapVal["3"]
                    price=mapVal["4"]
                    pickup_date=mapVal["5"]
                    delivery_date=mapVal["6"]
                    clat=mapVal["7"]
                    clng=mapVal["8"]
                    order_status=mapVal["9"]
                    delivery_epoch=mapVal["10"]
                    order_taken_epoch=mapVal["11"]
                    cancel_reason=mapVal["12"]
                    house_no=mapVal["13"]
                    address=mapVal["14"]

                    orderid_str=lst_to_str(orderid)
                    delivery_boyid_str=lst_to_str(delivery_boyid)
                    quantity_str=lst_to_str(quantity)
                    price_str=lst_to_str(price)
                    pickup_date_str=lst_to_str(pickup_date)
                    delivery_date_str=lst_to_str(delivery_date)
                    clat_str=lst_to_str(clat)
                    clng_str=lst_to_str(clng)
                    order_status_str=lst_to_str(order_status)
                    delivery_epoch_str=lst_to_str(delivery_epoch)
                    order_taken_epoch_str=lst_to_str(order_taken_epoch)
                    cancel_reason_str=lst_to_str(cancel_reason)
                    house_no_str=lst_to_str(house_no)
                    address_str=lst_to_str(address)

                    jdict={
                            "orderid":str(orderid_str),
                            "delivery_boyid":str(delivery_boyid_str),
                            "quantity":str(quantity_str),
                            "price":str(price_str),
                            "pickup_date":str(pickup_date_str),
                            "delivery_date":str(delivery_date),
                            "clat":str(clat_str),
                            "clng":str(clng_str),
                            "order_status":str(order_status_str),
                            "delivery_epoch":str(delivery_epoch_str),
                            "order_taken_epoch":str(order_taken_epoch_str),
                            "cancel_reason":str(cancel_reason_str),
                            "house_no":str(house_no_str),
                            "address":str(address_str),
                            }
                    return JsonResponse(jdict,safe=False)
        except KeyError as e:
            print(f"{Fore.RED}KeyError: {e}{Style.RESET_ALL} - Key does not exist in the JSON")
            return JsonResponse('ErrorCode#8',safe=False)
        except json.JSONDecodeError as e:
            print(f"{Fore.RED}Failed to parse JSON: {e}{Style.RESET_ALL}")
            return JsonResponse('ErrorCode#8',safe=False)
        except Exception as ex:
            print(f"{Style.RESET_ALL}Error fetching data: {ex}{Style.RESET_ALL}")
            return JsonResponse('ErrorCode#8',safe=False)

    return JsonResponse(reply_data,safe=False)



@csrf_exempt
def load_delivery_boy_all_orders_tab_details(request):
    global reply_data
    if request.method == "POST":
        try:
            jdict = json.loads(request.body)
            delivery_boy_id = jdict['delivery_boy_id']
            order_completed = jdict['order_completed']
            given_order_status = jdict['order_status']
            if given_order_status == 'Rejected':
                query = "select orderid,customerid,quantity,price,pickup_dt,delivery,clat,clng,order_status,delivery_epoch,laundry_ordertbl.epoch,cancel_reason,houseno,address,time as rejected_time from vff.laundry_delivery_accept_tbl,vff.laundry_customertbl,vff.usertbl,vff.laundry_delivery_boytbl,vff.laundry_ordertbl where usertbl.usrid=laundry_customertbl.usrid and laundry_ordertbl.delivery_boyid=laundry_delivery_accept_tbl.delivery_boy_id and laundry_delivery_accept_tbl.order_id=laundry_ordertbl.orderid and laundry_ordertbl.customerid=laundry_customertbl.consmrid and delivery_boyid='"+str(delivery_boy_id)+"'  and order_completed='0' and order_status='"+str(given_order_status)+"'  order by orderid desc"
            else:
                query = "select orderid,customerid,quantity,price,pickup_dt,delivery,clat,clng,order_status,delivery_epoch,laundry_ordertbl.epoch,cancel_reason,houseno,address from vff.laundry_customertbl,vff.usertbl,vff.laundry_ordertbl where usertbl.usrid=laundry_customertbl.usrid and laundry_ordertbl.customerid=laundry_customertbl.consmrid and delivery_boyid='"+str(delivery_boy_id)+"'   and order_completed='"+str(order_completed)+"' and order_status='"+str(given_order_status)+"'  order by orderid desc"
            if query != "":
                reply_data="ErrorCode#0"
                mapVal = execute_query_and_get_result(query)
                if mapVal != None:
                    orderid=mapVal["1"]
                    customer_id=mapVal["2"]
                    quantity=mapVal["3"]
                    price=mapVal["4"]
                    pickup_date=mapVal["5"]
                    delivery_date=mapVal["6"]
                    clat=mapVal["7"]
                    clng=mapVal["8"]
                    order_status=mapVal["9"]
                    delivery_epoch=mapVal["10"]
                    order_taken_epoch=mapVal["11"]
                    cancel_reason=mapVal["12"]
                    house_no=mapVal["13"]
                    address=mapVal["14"]


                    orderid_str=lst_to_str(orderid)
                    customer_id_str=lst_to_str(customer_id)
                    quantity_str=lst_to_str(quantity)
                    price_str=lst_to_str(price)
                    pickup_date_str=lst_to_str(pickup_date)
                    delivery_date_str=lst_to_str(delivery_date)
                    clat_str=lst_to_str(clat)
                    clng_str=lst_to_str(clng)
                    order_status_str=lst_to_str(order_status)
                    delivery_epoch_str=lst_to_str(delivery_epoch)
                    order_taken_epoch_str=lst_to_str(order_taken_epoch)
                    cancel_reason_str=lst_to_str(cancel_reason)
                    house_no_str=lst_to_str(house_no)
                    address_str=lst_to_str(address)

                    if given_order_status == "Rejected":
                        rejected_time = mapVal["15"]
                        rejected_time_str = lst_to_str(rejected_time)
                        jdict={
                            "orderid":str(orderid_str),
                            "customer_id":str(customer_id_str),
                            "quantity":str(quantity_str),
                            "price":str(price_str),
                            "pickup_date":str(pickup_date_str),
                            "delivery_date":str(delivery_date),
                            "clat":str(clat_str),
                            "clng":str(clng_str),
                            "order_status":str(order_status_str),
                            "delivery_epoch":str(delivery_epoch_str),
                            "order_taken_epoch":str(order_taken_epoch_str),
                            "cancel_reason":str(cancel_reason_str),
                            "house_no":str(house_no_str),
                            "address":str(address_str),
                            "rejected_time":str(rejected_time_str),
                            }
                    else:
                        jdict={
                            "orderid":str(orderid_str),
                            "customer_id":str(customer_id_str),
                            "quantity":str(quantity_str),
                            "price":str(price_str),
                            "pickup_date":str(pickup_date_str),
                            "delivery_date":str(delivery_date),
                            "clat":str(clat_str),
                            "clng":str(clng_str),
                            "order_status":str(order_status_str),
                            "delivery_epoch":str(delivery_epoch_str),
                            "order_taken_epoch":str(order_taken_epoch_str),
                            "cancel_reason":str(cancel_reason_str),
                            "house_no":str(house_no_str),
                            "address":str(address_str),
                            }
                    return JsonResponse(jdict,safe=False)
        except KeyError as e:
            print(f"{Fore.RED}KeyError: {e}{Style.RESET_ALL} - Key does not exist in the JSON")
            return JsonResponse('ErrorCode#8',safe=False)
        except json.JSONDecodeError as e:
            print(f"{Fore.RED}Failed to parse JSON: {e}{Style.RESET_ALL}")
            return JsonResponse('ErrorCode#8',safe=False)
        except Exception as ex:
            print(f"{Style.RESET_ALL}Error fetching data: {ex}{Style.RESET_ALL}")
            return JsonResponse('ErrorCode#8',safe=False)

    return JsonResponse(reply_data,safe=False)



@csrf_exempt
def delivery_boycurrent_active_order_details(request):
    global reply_data
    if request.method == "POST":
        try:
            jdict = json.loads(request.body)
            delivery_boy_id=jdict['delivery_boy_id']

            #query = "select orderid,customer_name,laundry_ordertbl.epoch,order_status,clat,clng,houseno,address,pincode,city,landmark,profile_img,device_token,mobile_no from vff.laundry_ordertbl,vff.laundry_order_historytbl,vff.laundry_delivery_boytbl,vff.laundry_customertbl,vff.usertbl where laundry_ordertbl.orderid=laundry_order_historytbl.order_id and (laundry_ordertbl.delivery_boyid=vff.laundry_delivery_boytbl.delivery_boy_id or  laundry_ordertbl.drop_delivery_boy_id=vff.laundry_delivery_boytbl.delivery_boy_id) and (drop_delivery_boy_id='"+str(delivery_boy_id)+"' or delivery_boy_id='"+str(delivery_boy_id)+"') and laundry_customertbl.consmrid=laundry_ordertbl.customerid and laundry_customertbl.usrid=usertbl.usrid and laundry_delivery_boytbl.status='Busy' and (order_stages='Accepted' or order_stages='Out for Delivery') AND date_trunc('day', to_timestamp(laundry_order_historytbl.time))::date = current_date limit 1"
            assigned_query="select booking_id,order_id,type_of_order from vff.laundry_order_assignmenttbl where delivery_boy_id='"+str(delivery_boy_id)+"' order by assign_id desc limit 1"
            if assigned_query != "":
                reply_data="ErrorCode#0"
                mapVal = execute_query_and_get_result(assigned_query)
                if mapVal != None:
                    assigned_booking_id=mapVal["1"]
                    assigned_order_id=mapVal["2"]
                    type_of_order=mapVal["3"]

                    if assigned_order_id[0] == "-1" and type_of_order[0] == "Pickup":
                        query1="select bookingid,customer_name,time_at,booking_status,laundry_order_bookingtbl.clat,laundry_order_bookingtbl.clng,houseno,laundry_order_bookingtbl.address,laundry_order_bookingtbl.pincode,laundry_order_bookingtbl.city,laundry_order_bookingtbl.landmark,profile_img,device_token,mobile_no,laundry_order_assignmenttbl.order_id,laundry_order_bookingtbl.customerid,laundry_order_bookingtbl.branch_id from vff.laundry_order_assignmenttbl,vff.laundry_order_bookingtbl,vff.laundry_delivery_boytbl,vff.usertbl,vff.laundry_customertbl where laundry_order_bookingtbl.delivery_boy_id=laundry_delivery_boytbl.delivery_boy_id  and laundry_order_assignmenttbl.booking_id=laundry_order_bookingtbl.bookingid and laundry_customertbl.consmrid=laundry_order_bookingtbl.customerid and laundry_customertbl.usrid=usertbl.usrid   and laundry_order_assignmenttbl.delivery_boy_id='"+str(delivery_boy_id)+"' and bookingid='"+str(assigned_booking_id[0])+"' and laundry_delivery_boytbl.status='Busy' and booking_status!='Cancelled' and laundry_order_assignmenttbl.order_id='-1' order by timing desc limit 1"
                        if query1 != "":
                            reply_data="ErrorCode#0"
                            mapVal = execute_query_and_get_result(query1)
                            if mapVal != None:
                                bookingid=mapVal["1"]
                                customer_name=mapVal["2"]
                                pickup_dt=mapVal["3"]
                                order_status=mapVal["4"]
                                clat=mapVal["5"]
                                clng=mapVal["6"]
                                houseno=mapVal["7"]
                                address=mapVal["8"]
                                pincode=mapVal["9"]
                                city=mapVal["10"]
                                landmark=mapVal["11"]
                                profile_img=mapVal["12"]
                                device_token=mapVal["13"]
                                mobile_no=mapVal["14"]
                                order_id=mapVal["15"]
                                customer_id=mapVal["16"]
                                branch_id=mapVal["17"]

                                orderid_str=lst_to_str(order_id)
                                customer_name_str=lst_to_str(customer_name)
                                pickup_dt_str=lst_to_str(pickup_dt)
                                order_status_str=lst_to_str(order_status)
                                clat_str=lst_to_str(clat)
                                clng_str=lst_to_str(clng)
                                house_no_str=lst_to_str(houseno)
                                address_str=lst_to_str(address)
                                pincode_str=lst_to_str(pincode)
                                city_str=lst_to_str(city)
                                landmark_str=lst_to_str(landmark)
                                profile_img_str=lst_to_str(profile_img)
                                device_token_str=lst_to_str(device_token)
                                mobile_no_str=lst_to_str(mobile_no)
                                booking_id_str=lst_to_str(bookingid)
                                customer_id_str=lst_to_str(customer_id)
                                branch_id_str=lst_to_str(branch_id)

                                jdict={
                                        "orderid":str(orderid_str),
                                        "customer_name":str(customer_name_str),
                                        "pickup_dt":str(pickup_dt_str),
                                        "order_status":str(order_status_str),
                                        "clat":str(clat_str),
                                        "clng":str(clng_str),
                                        "houseno":str(house_no_str),
                                        "address":str(address_str),
                                        "pincode":str(pincode_str),
                                        "city":str(city_str),
                                        "landmark":str(landmark_str),
                                        "profile_img":str(profile_img_str),
                                        "device_token":str(device_token_str),
                                        "mobile_no":str(mobile_no_str),
                                        "booking_id":str(booking_id_str),
                                        "customer_id":str(customer_id_str),
                                        "branch_id":str(branch_id_str),
                                        }
                                return JsonResponse(jdict,safe=False)
                    else:
            
                        query="select orderid,customer_name,laundry_ordertbl.epoch,order_status,laundry_order_bookingtbl.clat,laundry_order_bookingtbl.clng,houseno,laundry_order_bookingtbl.address,laundry_order_bookingtbl.pincode,laundry_order_bookingtbl.city,laundry_order_bookingtbl.landmark,profile_img,device_token,mobile_no,laundry_order_bookingtbl.bookingid,laundry_order_bookingtbl.customerid,laundry_order_bookingtbl.branch_id from vff.laundry_delivery_boytbl,vff.usertbl,vff.laundry_order_assignmenttbl,vff.laundry_order_bookingtbl,vff.laundry_ordertbl,vff.laundry_customertbl where laundry_ordertbl.delivery_boyid=laundry_delivery_boytbl.delivery_boy_id and  laundry_ordertbl.orderid=laundry_order_assignmenttbl.order_id and laundry_ordertbl.booking_id=laundry_order_bookingtbl.bookingid and laundry_order_assignmenttbl.booking_id=laundry_order_bookingtbl.bookingid and laundry_customertbl.consmrid=laundry_ordertbl.customerid and laundry_customertbl.usrid=usertbl.usrid and laundry_order_assignmenttbl.delivery_boy_id='"+str(delivery_boy_id)+"' and laundry_delivery_boytbl.status='Busy' order by timing desc limit 1"
                        if query != "":
                            reply_data="ErrorCode#0"
                            mapVal = execute_query_and_get_result(query)
                            if mapVal != None:
                                orderid=mapVal["1"]
                                customer_name=mapVal["2"]
                                pickup_dt=mapVal["3"]
                                order_status=mapVal["4"]
                                clat=mapVal["5"]
                                clng=mapVal["6"]
                                houseno=mapVal["7"]
                                address=mapVal["8"]
                                pincode=mapVal["9"]
                                city=mapVal["10"]
                                landmark=mapVal["11"]
                                profile_img=mapVal["12"]
                                device_token=mapVal["13"]
                                mobile_no=mapVal["14"]
                                booking_id=mapVal["15"]
                                customer_id=mapVal["16"]
                                branch_id=mapVal["17"]


                                orderid_str=lst_to_str(orderid)
                                customer_name_str=lst_to_str(customer_name)
                                pickup_dt_str=lst_to_str(pickup_dt)
                                order_status_str=lst_to_str(order_status)
                                clat_str=lst_to_str(clat)
                                clng_str=lst_to_str(clng)
                                house_no_str=lst_to_str(houseno)
                                address_str=lst_to_str(address)
                                pincode_str=lst_to_str(pincode)
                                city_str=lst_to_str(city)
                                landmark_str=lst_to_str(landmark)
                                profile_img_str=lst_to_str(profile_img)
                                device_token_str=lst_to_str(device_token)
                                mobile_no_str=lst_to_str(mobile_no)
                                booking_id_str=lst_to_str(booking_id)
                                customer_id_str=lst_to_str(customer_id)
                                branch_id_str=lst_to_str(branch_id)

                                jdict={
                                        "orderid":str(orderid_str),
                                        "customer_name":str(customer_name_str),
                                        "pickup_dt":str(pickup_dt_str),
                                        "order_status":str(order_status_str),
                                        "clat":str(clat_str),
                                        "clng":str(clng_str),
                                        "houseno":str(house_no_str),
                                        "address":str(address_str),
                                        "pincode":str(pincode_str),
                                        "city":str(city_str),
                                        "landmark":str(landmark_str),
                                        "profile_img":str(profile_img_str),
                                        "device_token":str(device_token_str),
                                        "mobile_no":str(mobile_no_str),
                                        "booking_id":str(booking_id_str),
                                        "customer_id":str(customer_id_str),
                                        "branch_id":str(branch_id_str),
                                        }
                                return JsonResponse(jdict,safe=False)
        except KeyError as e:
            print(f"{Fore.RED}KeyError: {e}{Style.RESET_ALL} - Key does not exist in the JSON")
            return JsonResponse('ErrorCode#8',safe=False)
        except json.JSONDecodeError as e:
            print(f"{Fore.RED}Failed to parse JSON: {e}{Style.RESET_ALL}")
            return JsonResponse('ErrorCode#8',safe=False)
        except Exception as ex:
            print(f"{Style.RESET_ALL}Error fetching data: {ex}{Style.RESET_ALL}")
            return JsonResponse('ErrorCode#8',safe=False)

    return JsonResponse(reply_data,safe=False)



@csrf_exempt
def send_notification_to_assigned_delivery_boy_for_booking(request,sender_id,mtitle,mbody,mintent,bookingid,mdata):
    query = "select usrname,mobile_no,profile_img,device_token,laundry_delivery_boytbl.delivery_boy_id from vff.usertbl,vff.laundry_delivery_boytbl,vff.laundry_order_bookingtbl where laundry_delivery_boytbl.usrid=usertbl.usrid and laundry_order_bookingtbl.delivery_boy_id=laundry_delivery_boytbl.delivery_boy_id  and bookingid='"+str(bookingid)+"'"

    if query != None:
        mapVal = execute_query_and_get_result(query)
        if mapVal != None:
            username=mapVal["1"]
            mobile_no=mapVal["2"]
            profile_img=mapVal["3"]
            device_token=mapVal["4"]
            delivery_boy_id=mapVal["5"]
        if bookingid != "":
            title =mtitle
            body = mbody
            intent=mintent
            query2="insert into vff.laundry_notificationtbl(title,body,intent,reciever_id,sender_id,booking_id) values ('"+str(title)+"','"+str(body)+"','"+str(intent)+"','"+str(delivery_boy_id[0])+"','"+str(sender_id)+"','"+str(bookingid)+"')"
        try:
            with connection.cursor() as cursor:
                cursor.execute(query2)
                connection.commit()
                #send notification to Delivery Boy
                try:
                    print('Sending Notification to delivery boy')
                    data = mdata
                    sendFMCMsg(device_token[0],body,title,data)
                except Exception as e:
                    print('Error Sending Notification')
                    print(e)
        except Exception as e:
             print('Error Inserting Notification record for delivery boy')
             print(e)



@csrf_exempt
def send_notification_to_assigned_delivery_boy(request,sender_id,mtitle,mbody,mintent,orderid,mdata):
    global reply_data
    query = "select usrname,mobile_no,profile_img,device_token,laundry_delivery_boytbl.delivery_boy_id from vff.usertbl,vff.laundry_delivery_boytbl,vff.laundry_ordertbl where laundry_delivery_boytbl.usrid=usertbl.usrid and laundry_ordertbl.delivery_boyid=laundry_delivery_boytbl.delivery_boy_id  and orderid='"+str(orderid)+"'"

    if query != None:
        mapVal = execute_query_and_get_result(query)
        if mapVal != None:
            username=mapVal["1"]
            mobile_no=mapVal["2"]
            profile_img=mapVal["3"]
            device_token=mapVal["4"]
            delivery_boy_id=mapVal["5"]
        if orderid != "":
            title =mtitle
            body = mbody
            intent=mintent
            query2="insert into vff.laundry_notificationtbl(title,body,intent,reciever_id,sender_id,order_id) values ('"+str(title)+"','"+str(body)+"','"+str(intent)+"','"+str(delivery_boy_id)+"','"+str(sender_id)+"','"+str(orderid)+"')"
        try:
            with connection.cursor() as cursor:
                cursor.execute(query)
                connection.commit()
                #send notification to Delivery Boy
                try:
                    print('Sending Notification to delivery boy')
                    data = mdata
                    sendFMCMsg(device_token[0],body,title,data)
                except Exception as e:
                    print('Error Sending Notification')
                    print(e)
        except Exception as e:
             print('Error Inserting Notification record for delivery boy')
             print(e)



@csrf_exempt
def send_notification_to_customer_with_bookingid(request,sender_id,mtitle,mbody,mintent,booking_id,mdata):
    global reply_data
    query="select usrname,mobile_no,profile_img,device_token,laundry_order_bookingtbl.customerid from vff.usertbl,vff.laundry_customertbl,vff.laundry_order_bookingtbl where laundry_customertbl.usrid=usertbl.usrid and laundry_order_bookingtbl.customerid=laundry_customertbl.consmrid and bookingid='"+str(booking_id)+"'"
    if query != None:
        mapVal = execute_query_and_get_result(query)
        if mapVal != None:
            username=mapVal["1"]
            mobile_no=mapVal["2"]
            profile_img=mapVal["3"]
            device_token=mapVal["4"]
            customer_id=mapVal["5"]
        if booking_id != "":
            title =mtitle
            body = mbody
            intent=mintent
            query2="insert into vff.laundry_notificationtbl(title,body,intent,reciever_id,sender_id,booking_id) values ('"+str(title)+"','"+str(body)+"','"+str(intent)+"','"+str(customer_id[0])+"','"+str(sender_id)+"','"+str(booking_id)+"')"
        try:
            with connection.cursor() as cursor:
                cursor.execute(query2)
                connection.commit()
                #send Customer Notification
                try:
                    print('Sending Notification to customer')
                    data = mdata
                    sendFMCMsg(device_token[0],body,title,data)
                except Exception as e:
                    print('Error Sending Notification')
                    print(e)
        except Exception as e:
             print('Error Inserting Notification record for customer')
             print(e)



@csrf_exempt
def send_notification_to_customer(request,sender_id,mtitle,mbody,mintent,orderid,mdata):
    global reply_data
    query = "select usrname,mobile_no,profile_img,device_token,laundry_ordertbl.customerid from vff.usertbl,vff.laundry_customertbl,vff.laundry_ordertbl where laundry_customertbl.usrid=usertbl.usrid and laundry_ordertbl.customerid=laundry_customertbl.consmrid and orderid='"+str(orderid)+"'"

    if query != None:
        mapVal = execute_query_and_get_result(query)
        if mapVal != None:
            username=mapVal["1"]
            mobile_no=mapVal["2"]
            profile_img=mapVal["3"]
            device_token=mapVal["4"]
            customer_id=mapVal["5"]
        if orderid != "":
            title =mtitle
            body = mbody
            intent=mintent
            query2="insert into vff.laundry_notificationtbl(title,body,intent,reciever_id,sender_id,order_id) values ('"+str(title)+"','"+str(body)+"','"+str(intent)+"','"+str(customer_id[0])+"','"+str(sender_id)+"','"+str(orderid)+"')"
        try:
            with connection.cursor() as cursor:
                cursor.execute(query2)
                connection.commit()
                 #send Customer Notification
                try:
                     print('Sending Notification to customer')
                     data = mdata
                     sendFMCMsg(device_token[0],body,title,data)
                except Exception as e:
                     print('Error Sending Notification')
                     print(e)
        except Exception as e:
             print('Error Inserting Notification record for customer')
             print(e)



@csrf_exempt
def update_current_order_status(request):
    global reply_data
    jdict=json.loads(request.body)
    order_status = jdict['order_status']
    order_id = jdict['order_id']
    delivery_boy_id = jdict['delivery_boy_id']
    order_completed = "0"

    orderid = order_id
    if 'pickup_completed' in jdict:
        pickup_completed=jdict['pickup_completed']
        print(f'pickup_completed::{pickup_completed}')
        update_order_details="update vff.laundry_order_assignmenttbl set pickup_done='1' where order_id='"+str(order_id)+"' and type_of_order='Pickup'"
        try:
            with connection.cursor() as cursor:
                cursor.execute(update_order_details)
                connection.commit()
        except Exception as e:
            print(e)
            print('Error while updating pickup status')
    if 'delivery_completed' in jdict:
        delivery_completed=jdict['delivery_completed']
        update_completed_details="update vff.laundry_order_assignmenttbl set order_delivered='1' where order_id='"+str(order_id)+"' and type_of_order='Drop'"
        try:
            with connection.cursor() as cursor:
                cursor.execute(update_completed_details)
                connection.commit()
        except Exception as e:
            print(e)
            print('Error while updating drop order status')

    filterc=""
    if order_status == "Completed":
        order_completed = "1"
        current_timestamp = time.time()
        filterc=",delivery_boyid='"+str(delivery_boy_id)+"',delivery_epoch='"+str(current_timestamp)+"'"
    query = "update vff.laundry_ordertbl set order_status='"+str(order_status)+"',order_completed='"+str(order_completed)+"' "+filterc+" where orderid='"+str(order_id)+"'"
    try:
        with connection.cursor() as cursor:
            cursor.execute(query)
            connection.commit()
        #obj.reply_data="ErrorCode#0"
        #Updates in Order history table as well
        orderid = order_id
        if order_status == "Completed":
            #Sending Notification to Delivery Boy i.e he is free to take new orders
            dtitle="Delivery Done"
            dmsg="You have successfully delivered the laundry package. Now you are free to take new orders"
            data={
                    'order_id':str(order_id)
                    }
            send_notification_to_assigned_delivery_boy(request,'1',dtitle,dmsg,'MainRoute',order_id,data)

            title="Order Completed"
            message="Laundry Package Delivery Successfully for Order ID : #"+str(orderid)+" . Keep Ordering with Velvet Wash"
            data={
                    'order_id':str(orderid)
                    }
            #Free Delivery Boy
            query4 = "update vff.laundry_delivery_boytbl set status='Free'  where delivery_boy_id='"+str(delivery_boy_id)+"'"
            try:
                with connection.cursor() as cursor:
                    cursor.execute(query4)
                    connection.commit()
                reply_data="ErrorCode#0"
            except Exception as e:
                print(e)
                reply_data="ErrorCode#8"

        elif order_status == "Reached Store":
            title="Reached Store"
            print(f'OrderID:{orderid}')
            message="Laundry Package has reached store for Order ID #"+str(orderid)+". We will keep you posted at every stage of process.Thank you"
            data={
                'order_id':str(orderid)
                }
            #Free Delivery Boy
            query5 = "update vff.laundry_delivery_boytbl set status='Free'  where delivery_boy_id='"+str(delivery_boy_id)+"'"
            try:
                with connection.cursor() as cursor:
                    cursor.execute(query5)
                    connection.commit()
                    reply_data="ErrorCode#0"
            except Exception as e:
                print(e)
                reply_data="ErrorCode#8"
        else:

            title="Pickup Done Successfully"
            print(f'OrderID:{orderid}')
            message="Laundry Pick up done Successfully for Order ID #"+str(orderid)+". We will keep you posted at every stage of process.Thank you"
            data={
                'order_id':str(orderid)
                }
        intent = "MainRoute"
        send_notification_to_customer(request,delivery_boy_id,title,message,intent,order_id,data)
        update_order_status(request,orderid,order_status)

    except Exception as e:
        print(e)
        reply_data ="ErrorCode#8"

    return JsonResponse(reply_data,safe=False)



@csrf_exempt
def update_current_new_booking_status(request):
    global reply_data
    jdict=json.loads(request.body)
    booking_status = jdict['booking_status']
    booking_id = jdict['booking_id']
    delivery_boy_id = jdict['delivery_boy_id']
    order_completed = "0"

    if 'pickup_completed' in jdict:
        pickup_completed=jdict['pickup_completed']
        print(f'pickup_completed::{pickup_completed}')
        update_order_details="update vff.laundry_order_assignmenttbl set pickup_done='1' where booking_id='"+str(booking_id)+"' and type_of_order='Pickup'"
        try:
            with connection.cursor() as cursor:
                cursor.execute(update_order_details)
                connection.commit()
        except Exception as e:
            print(e)
            print('Error while updating pickup status')
    if 'delivery_completed' in jdict:
        delivery_completed=jdict['delivery_completed']
        update_completed_details="update vff.laundry_order_assignmenttbl set order_delivered='1' where booking_id='"+str(booking_id)+"' and type_of_order='Drop'"
        try:
            with connection.cursor() as cursor:
                cursor.execute(update_completed_details)
                connection.commit()
        except Exception as e:
            print(e)
            print('Error while updating drop order status')

    filterc=""
    try:
        if booking_status == "Reached Store":
            title="Reached Store"
            message="Laundry Package has reached store for Booking ID #"+str(booking_id)+". We will keep you posted at every stage of process.Thank you"
            data={
                'booking_id':str(booking_id)
                }
            #Free Delivery Boy
            query5 = "update vff.laundry_delivery_boytbl set status='Free'  where delivery_boy_id='"+str(delivery_boy_id)+"'"
            try:
                with connection.cursor() as cursor:
                    cursor.execute(query5)
                    connection.commit()
                    reply_data="ErrorCode#0"
            except Exception as e:
                print(e)
                reply_data="ErrorCode#8"
        elif booking_status == "Reached Pickup Location":
            title="Reached Pickup Location"
            message="Our Delivery Agent has arrived at the pickup destination.Please handover the Laundry."
            data={
                'booking_id':str(booking_id)
                }



        elif booking_status == "Pick Up Done":
            title="Pick Up Done"
            message="Your laundry Package has been pickup by our delivery agent."
            data={
                'booking_id':str(booking_id)
                }

        intent = "MainRoute"


        send_notification_to_customer_with_bookingid(request,delivery_boy_id,title,message,intent,booking_id,data)
        #update_order_status(obj,orderid,order_status)
        update_booking_status(request,booking_id,booking_status)
        
    except Exception as e:
        print(e)
        reply_data ="ErrorCode#8"

    return JsonResponse(reply_data,safe=False)




@csrf_exempt
def load_todays_notifications(request):
    global reply_data
    if request.method == "POST":
        try:
            jdict = json.loads(request.body)
            cusmr_devlry_id=jdict['customerordeliveryboyid']
            query="select notification_id,title,body,epoch,order_id,intent,booking_id from vff.laundry_notificationtbl where reciever_id='"+str(cusmr_devlry_id)+"' and date=CURRENT_DATE order by notification_id desc"
            if query != "":
                reply_data="ErrorCode#0"
                mapVal = execute_query_and_get_result(query)
                if mapVal != None:
                    notify_id=mapVal["1"]
                    title=mapVal["2"]
                    body=mapVal["3"]
                    epoch_time=mapVal["4"]
                    order_id=mapVal["5"]
                    intent=mapVal["6"]
                    booking_id=mapVal["7"]

                    notify_id_str=lst_to_str(notify_id)
                    title_str=lst_to_str(title)
                    body_str=lst_to_str(body)
                    epoch_time_str=lst_to_str(epoch_time)
                    order_id_str=lst_to_str(order_id)
                    intent_str=lst_to_str(intent)
                    booking_id_str=lst_to_str(booking_id)

                    jdict={
                            "notify_id":str(notify_id_str),
                            "title":str(title_str),
                            "body":str(body_str),
                            "epoch_time":str(epoch_time_str),
                            "order_id":str(order_id_str),
                            "intent":str(intent_str),
                            "booking_id":str(booking_id_str),
                            }
                    return JsonResponse(jdict,safe=False)
        except KeyError as e:
            print(f"{Fore.RED}KeyError: {e}{Style.RESET_ALL} - Key does not exist in the JSON")
            return JsonResponse('ErrorCode#8',safe=False)
        except json.JSONDecodeError as e:
            print(f"{Fore.RED}Failed to parse JSON: {e}{Style.RESET_ALL}")
            return JsonResponse('ErrorCode#8',safe=False)
        except Exception as ex:
            print(f"{Style.RESET_ALL}Error fetching data: {ex}{Style.RESET_ALL}")
            return JsonResponse('ErrorCode#8',safe=False)

    return JsonResponse(reply_data,safe=False)



@csrf_exempt
def delivery_boy_stats(request):
    global reply_data
    if request.method == "POST":
        try:
            jdict = json.loads(request.body)
            delivery_boy_id=jdict['deliveryboyid']
            #Total Orders Completed
            #query="select count(*) from vff.laundry_customertbl,vff.usertbl,vff.laundry_ordertbl where usertbl.usrid=laundry_customertbl.usrid and laundry_ordertbl.customerid=laundry_customertbl.consmrid and delivery_boyid='"+str(delivery_boy_id)+"'  and order_completed='1' and order_status='Completed'"
            query="select count(*) from vff.laundry_order_assignmenttbl where delivery_boy_id='"+str(delivery_boy_id)+"' and type_of_order='Pickup'"
            if query != "":
                reply_data="ErrorCode#0"
                mapVal = execute_query_and_get_result(query)
                if mapVal != None:
                    total_completed=mapVal["1"]

                    total_completed_str=lst_to_str(total_completed)
                    #query2="select count(*) from vff.laundry_customertbl,vff.usertbl,vff.laundry_ordertbl where usertbl.usrid=laundry_customertbl.usrid and laundry_ordertbl.customerid=laundry_customertbl.consmrid and delivery_boyid='"+str(delivery_boy_id)+"'  and order_completed='0' and order_status='Rejected'"
                    query2="select count(*) from vff.laundry_order_assignmenttbl where delivery_boy_id='"+str(delivery_boy_id)+"' and type_of_order='Drop'"
                    if query2 != "":
                        reply_data="ErrorCode#0"
                        mapVal = execute_query_and_get_result(query2)
                        if mapVal != None:
                            total_rejected=mapVal["1"]
                            total_rejected_str=lst_to_str(total_rejected)

                            query3="select count(*) from vff.laundry_customertbl,vff.usertbl,vff.laundry_ordertbl where usertbl.usrid=laundry_customertbl.usrid and laundry_ordertbl.customerid=laundry_customertbl.consmrid and delivery_boyid='"+str(delivery_boy_id)+"'  and order_completed='0' and order_status='Accepted'"
                            if query3 != "":
                                reply_data="ErrorCode#0"
                                mapVal = execute_query_and_get_result(query3)
                                if mapVal != None:
                                    total_ongoing=mapVal["1"]
                                    total_ongoing_str=lst_to_str(total_ongoing)

                                    query4 ="select count(*) from vff.laundry_customertbl,vff.usertbl,vff.laundry_ordertbl where usertbl.usrid=laundry_customertbl.usrid and laundry_ordertbl.customerid=laundry_customertbl.consmrid and delivery_boyid='"+str(delivery_boy_id)+"'  and order_completed='0' and order_status='Cancelled'"
                                    if query4 != "":
                                        reply_data="ErrorCode#0"
                                        mapVal = execute_query_and_get_result(query4)
                                        if mapVal != None:
                                            total_returned=mapVal["1"]
                                            total_returned_str=lst_to_str(total_returned)

                    jdict={
                            "total_pickup":str(total_completed_str),
                            "total_drop":str(total_rejected_str),
                            "total_ongoing":str(total_ongoing_str),
                            "total_returned":str(total_returned_str),
                            }
                    return JsonResponse(jdict,safe=False)
        except KeyError as e:
            print(f"{Fore.RED}KeyError: {e}{Style.RESET_ALL} - Key does not exist in the JSON")
            return JsonResponse('ErrorCode#8',safe=False)
        except json.JSONDecodeError as e:
            print(f"{Fore.RED}Failed to parse JSON: {e}{Style.RESET_ALL}")
            return JsonResponse('ErrorCode#8',safe=False)
        except Exception as ex:
            print(f"{Style.RESET_ALL}Error fetching data: {ex}{Style.RESET_ALL}")
            return JsonResponse('ErrorCode#8',safe=False)

    return JsonResponse(reply_data,safe=False)



@csrf_exempt
def load_all_branches(request):
    global reply_data
    if request.method == "POST":
        try:
            jdict = json.loads(request.body)
            query="select branchid,branch_name,address,city,state,pincode from vff.branchtbl where status='1'"
            if query != "":
                reply_data="ErrorCode#0"
                mapVal = execute_query_and_get_result(query)
                if mapVal != None:
                    branch_id=mapVal["1"]
                    branch_name=mapVal["2"]
                    address=mapVal["3"]
                    city=mapVal["4"]
                    state=mapVal["5"]
                    pincode=mapVal["6"]

                    branch_id_str=lst_to_str(branch_id)
                    branch_name_str=lst_to_str(branch_name)
                    address_str=lst_to_str(address)
                    city_str=lst_to_str(city)
                    state_str=lst_to_str(state)
                    pincode_str=lst_to_str(pincode)

                    jdict={
                            "branch_id":str(branch_id_str),
                            "branch_name":str(branch_name_str),
                            "address":str(address_str),
                            "city":str(city_str),
                            "state":str(state_str),
                            "pincode":str(pincode_str),
                            }
                    return JsonResponse(jdict,safe=False)
        except KeyError as e:
            print(f"{Fore.RED}KeyError: {e}{Style.RESET_ALL} - Key does not exist in the JSON")
            return JsonResponse('ErrorCode#8',safe=False)
        except json.JSONDecodeError as e:
            print(f"{Fore.RED}Failed to parse JSON: {e}{Style.RESET_ALL}")
            return JsonResponse('ErrorCode#8',safe=False)
        except Exception as ex:
            print(f"{Style.RESET_ALL}Error fetching data: {ex}{Style.RESET_ALL}")
            return JsonResponse('ErrorCode#8',safe=False)

    return JsonResponse(reply_data,safe=False)


@csrf_exempt
def load_all_pickup_order(request):
    global reply_data
    if request.method == "POST":
        try:
            jdict = json.loads(request.body)
            delivery_boy_id=jdict['delivery_boy_id']
            branch_id=jdict['branch_id']
            query="select booking_id,customer_name,laundry_order_bookingtbl.address,laundry_order_bookingtbl.city,laundry_order_bookingtbl.pincode,laundry_order_bookingtbl.landmark,order_id,branch_name,branchtbl.address from vff.laundry_order_assignmenttbl,vff.laundry_order_bookingtbl,vff.laundry_customertbl,vff.branchtbl where laundry_order_assignmenttbl.delivery_boy_id=laundry_order_bookingtbl.delivery_boy_id and laundry_order_bookingtbl.customerid=laundry_customertbl.consmrid and laundry_order_assignmenttbl.booking_id=laundry_order_bookingtbl.bookingid and branchtbl.branchid=laundry_order_bookingtbl.branch_id  and laundry_order_assignmenttbl.delivery_boy_id='"+str(delivery_boy_id)+"' and order_delivered='0' and type_of_order='Pickup' and pickup_done='0'   order by assign_id desc"
            #query="select booking_id,customer_name,address,city,pincode,landmark,order_id from vff.laundry_order_assignmenttbl,vff.laundry_order_bookingtbl,vff.laundry_customertbl where laundry_order_assignmenttbl.delivery_boy_id=laundry_order_bookingtbl.delivery_boy_id and laundry_order_bookingtbl.customerid=laundry_customertbl.consmrid and laundry_order_assignmenttbl.booking_id=laundry_order_bookingtbl.bookingid  and laundry_order_assignmenttbl.delivery_boy_id='"+str(delivery_boy_id)+"' and order_delivered='0' and type_of_order='Pickup' and pickup_done='0' and branch_id='"+str(branch_id)+"'  order by assign_id desc"
            if query != "":
                reply_data="ErrorCode#0"
                mapVal = execute_query_and_get_result(query)
                if mapVal != None:
                    booking_id=mapVal["1"]
                    customer_name=mapVal["2"]
                    address=mapVal["3"]
                    city=mapVal["4"]
                    pincode=mapVal["5"]
                    landmark=mapVal["6"]
                    order_id=mapVal["7"]
                    branch_name=mapVal["8"]
                    branch_address=mapVal["9"]

                    booking_id_str=lst_to_str(booking_id)
                    customer_name_str=lst_to_str(customer_name)
                    address_str=lst_to_str(address)
                    city_str=lst_to_str(city)
                    pincode_str=lst_to_str(pincode)
                    landmark_str=lst_to_str(landmark)
                    order_id_str=lst_to_str(order_id)
                    branch_name_str=lst_to_str(branch_name)
                    branch_address_str=lst_to_str(branch_address)

                    jdict={
                            "booking_id":str(booking_id_str),
                            "customer_name":str(customer_name_str),
                            "address":str(address_str),
                            "city":str(city_str),
                            "landmark":str(landmark_str),
                            "pincode":str(pincode_str),
                            "order_id":str(order_id_str),
                            "branch_name":str(branch_name_str),
                            "branch_address":str(branch_address_str),
                            }
                    return JsonResponse(jdict,safe=False)
        except KeyError as e:
            print(f"{Fore.RED}KeyError: {e}{Style.RESET_ALL} - Key does not exist in the JSON")
            return JsonResponse('ErrorCode#8',safe=False)
        except json.JSONDecodeError as e:
            print(f"{Fore.RED}Failed to parse JSON: {e}{Style.RESET_ALL}")
            return JsonResponse('ErrorCode#8',safe=False)
        except Exception as ex:
            print(f"{Style.RESET_ALL}Error fetching data: {ex}{Style.RESET_ALL}")
            return JsonResponse('ErrorCode#8',safe=False)

    return JsonResponse(reply_data,safe=False)




@csrf_exempt
def load_all_drop_order(request):
    global reply_data
    if request.method == "POST":
        try:
            jdict = json.loads(request.body)
            delivery_boy_id=jdict['delivery_boy_id']
            branch_id=jdict['branch_id']
            query="select order_id,customer_name,laundry_order_bookingtbl.address,laundry_order_bookingtbl.city,laundry_order_bookingtbl.pincode,laundry_order_bookingtbl.landmark,branch_name,branchtbl.address from vff.laundry_order_assignmenttbl,vff.laundry_order_bookingtbl,vff.laundry_customertbl,vff.branchtbl where laundry_order_assignmenttbl.delivery_boy_id=laundry_order_bookingtbl.delivery_boy_id and laundry_order_bookingtbl.customerid=laundry_customertbl.consmrid and laundry_order_assignmenttbl.booking_id=laundry_order_bookingtbl.bookingid  and laundry_order_assignmenttbl.delivery_boy_id='"+str(delivery_boy_id)+"' and order_delivered='0' and type_of_order='Drop'  order by assign_id desc"
            #query="select order_id,customer_name,address,city,pincode,landmark from vff.laundry_order_assignmenttbl,vff.laundry_order_bookingtbl,vff.laundry_customertbl where laundry_order_assignmenttbl.delivery_boy_id=laundry_order_bookingtbl.delivery_boy_id and laundry_order_bookingtbl.customerid=laundry_customertbl.consmrid and laundry_order_assignmenttbl.booking_id=laundry_order_bookingtbl.bookingid  and laundry_order_assignmenttbl.delivery_boy_id='"+str(delivery_boy_id)+"' and order_delivered='0' and type_of_order='Drop' and branch_id='"+str(branch_id)+"'  order by assign_id desc"
            if query != "":
                reply_data="ErrorCode#0"
                mapVal = execute_query_and_get_result(query)
                if mapVal != None:
                    order_id=mapVal["1"]
                    customer_name=mapVal["2"]
                    address=mapVal["3"]
                    city=mapVal["4"]
                    pincode=mapVal["5"]
                    landmark=mapVal["6"]
                    branch_name=mapVal["7"]
                    branch_address=mapVal["8"]

                    order_id_str=lst_to_str(order_id)
                    customer_name_str=lst_to_str(customer_name)
                    address_str=lst_to_str(address)
                    city_str=lst_to_str(city)
                    pincode_str=lst_to_str(pincode)
                    landmark_str=lst_to_str(landmark)
                    branch_name_str=lst_to_str(branch_name)
                    branch_address_str=lst_to_str(branch_address)

                    jdict={
                            "order_id":str(order_id_str),
                            "customer_name":str(customer_name_str),
                            "address":str(address_str),
                            "city":str(city_str),
                            "landmark":str(landmark_str),
                            "pincode":str(pincode_str),
                            "branch_name":str(branch_name_str),
                            "branch_address":str(branch_address_str),
                            }
                    return JsonResponse(jdict,safe=False)
        except KeyError as e:
            print(f"{Fore.RED}KeyError: {e}{Style.RESET_ALL} - Key does not exist in the JSON")
            return JsonResponse('ErrorCode#8',safe=False)
        except json.JSONDecodeError as e:
            print(f"{Fore.RED}Failed to parse JSON: {e}{Style.RESET_ALL}")
            return JsonResponse('ErrorCode#8',safe=False)
        except Exception as ex:
            print(f"{Style.RESET_ALL}Error fetching data: {ex}{Style.RESET_ALL}")
            return JsonResponse('ErrorCode#8',safe=False)

    return JsonResponse(reply_data,safe=False)


@csrf_exempt
def load_all_pickup_or_drop_booking_details(request):
    global reply_data
    if request.method == "POST":
        try:
            jdict = json.loads(request.body)
            delivery_boy_id=jdict['delivery_boy_id']
            order_id=jdict['order_id']#it can be booking id or order id
            order_type=jdict['order_type']
            booking_to_order_id=jdict['booking_to_order_id']
            if order_type=='Pickup':
                query="select bookingid,customer_name,time_at,booking_status,laundry_order_bookingtbl.clat,laundry_order_bookingtbl.clng,houseno,laundry_order_bookingtbl.address,laundry_order_bookingtbl.pincode,laundry_order_bookingtbl.city,laundry_order_bookingtbl.landmark,profile_img,device_token,mobile_no,laundry_order_assignmenttbl.order_id,laundry_order_bookingtbl.customerid,laundry_order_bookingtbl.branch_id from vff.laundry_order_assignmenttbl,vff.laundry_order_bookingtbl,vff.laundry_delivery_boytbl,vff.usertbl,vff.laundry_customertbl where laundry_order_bookingtbl.delivery_boy_id=laundry_delivery_boytbl.delivery_boy_id  and laundry_order_assignmenttbl.booking_id=laundry_order_bookingtbl.bookingid and laundry_customertbl.consmrid=laundry_order_bookingtbl.customerid and laundry_customertbl.usrid=usertbl.usrid   and laundry_order_assignmenttbl.delivery_boy_id='"+str(delivery_boy_id)+"'  and booking_status!='Cancelled'  and laundry_order_bookingtbl.bookingid='"+str(order_id)+"' order by timing desc "
            elif order_type=='Drop' and booking_to_order_id=='Yes':
                query="select orderid,customer_name,laundry_ordertbl.epoch,order_status,laundry_order_bookingtbl.clat,laundry_order_bookingtbl.clng,houseno,laundry_order_bookingtbl.address,laundry_order_bookingtbl.pincode,laundry_order_bookingtbl.city,laundry_order_bookingtbl.landmark,profile_img,device_token,mobile_no,laundry_order_bookingtbl.bookingid,laundry_order_bookingtbl.customerid,laundry_order_bookingtbl.branch_id from vff.laundry_delivery_boytbl,vff.usertbl,vff.laundry_order_assignmenttbl,vff.laundry_order_bookingtbl,vff.laundry_ordertbl,vff.laundry_customertbl where laundry_ordertbl.delivery_boyid=laundry_delivery_boytbl.delivery_boy_id and  laundry_ordertbl.orderid=laundry_order_assignmenttbl.order_id and laundry_ordertbl.booking_id=laundry_order_bookingtbl.bookingid and laundry_order_assignmenttbl.booking_id=laundry_order_bookingtbl.bookingid and laundry_customertbl.consmrid=laundry_ordertbl.customerid and laundry_customertbl.usrid=usertbl.usrid and laundry_order_assignmenttbl.delivery_boy_id='"+str(delivery_boy_id)+"' and laundry_ordertbl.orderid='"+str(order_id)+"'"
            else:
                query="select orderid,customer_name,laundry_ordertbl.epoch,order_status,laundry_order_bookingtbl.clat,laundry_order_bookingtbl.clng,houseno,laundry_order_bookingtbl.address,laundry_order_bookingtbl.pincode,laundry_order_bookingtbl.city,laundry_order_bookingtbl.landmark,profile_img,device_token,mobile_no,laundry_order_bookingtbl.bookingid,laundry_order_bookingtbl.customerid,laundry_order_bookingtbl.branch_id from vff.laundry_delivery_boytbl,vff.usertbl,vff.laundry_order_assignmenttbl,vff.laundry_order_bookingtbl,vff.laundry_ordertbl,vff.laundry_customertbl where laundry_ordertbl.delivery_boyid=laundry_delivery_boytbl.delivery_boy_id and  laundry_ordertbl.orderid=laundry_order_assignmenttbl.order_id and laundry_ordertbl.booking_id=laundry_order_bookingtbl.bookingid and laundry_order_assignmenttbl.booking_id=laundry_order_bookingtbl.bookingid and laundry_customertbl.consmrid=laundry_ordertbl.customerid and laundry_customertbl.usrid=usertbl.usrid and laundry_order_assignmenttbl.delivery_boy_id='"+str(delivery_boy_id)+"' and laundry_ordertbl.orderid='"+str(order_id)+"' and type_of_order='Drop' order by timing desc"
            if query != "":
                reply_data="ErrorCode#0"
                mapVal = execute_query_and_get_result(query)
                if mapVal != None:
                    if order_type=='Pickup':
                        bookingid=mapVal["1"]
                        order_id=mapVal["15"]
                    else:
                        order_id=mapVal["1"]
                        bookingid=mapVal["15"]
                    customer_name=mapVal["2"]
                    pickup_dt=mapVal["3"]
                    order_status=mapVal["4"]
                    clat=mapVal["5"]
                    clng=mapVal["6"]
                    houseno=mapVal["7"]
                    address=mapVal["8"]
                    pincode=mapVal["9"]
                    city=mapVal["10"]
                    landmark=mapVal["11"]
                    profile_img=mapVal["12"]
                    device_token=mapVal["13"]
                    mobile_no=mapVal["14"]
                    customer_id=mapVal["16"]
                    branch_id=mapVal["17"]

                    orderid_str=lst_to_str(order_id)
                    customer_name_str=lst_to_str(customer_name)
                    pickup_dt_str=lst_to_str(pickup_dt)
                    order_status_str=lst_to_str(order_status)
                    clat_str=lst_to_str(clat)
                    clng_str=lst_to_str(clng)
                    house_no_str=lst_to_str(houseno)
                    address_str=lst_to_str(address)
                    pincode_str=lst_to_str(pincode)
                    city_str=lst_to_str(city)
                    landmark_str=lst_to_str(landmark)
                    profile_img_str=lst_to_str(profile_img)
                    device_token_str=lst_to_str(device_token)
                    mobile_no_str=lst_to_str(mobile_no)
                    booking_id_str=lst_to_str(bookingid)
                    customer_id_str=lst_to_str(customer_id)
                    branch_id_str=lst_to_str(branch_id)
                    jdict={
                            "orderid":str(orderid_str),
                            "customer_name":str(customer_name_str),
                            "pickup_dt":str(pickup_dt_str),
                            "order_status":str(order_status_str),
                            "clat":str(clat_str),
                            "clng":str(clng_str),
                            "houseno":str(house_no_str),
                            "address":str(address_str),
                            "pincode":str(pincode_str),
                            "city":str(city_str),
                            "landmark":str(landmark_str),
                            "profile_img":str(profile_img_str),
                            "device_token":str(device_token_str),
                            "mobile_no":str(mobile_no_str),
                            "booking_id":str(booking_id_str),
                            "customer_id":str(customer_id_str),
                            "branch_id":str(branch_id_str),
                    }
                    return JsonResponse(jdict,safe=False)
        except KeyError as e:
            print(f"{Fore.RED}KeyError: {e}{Style.RESET_ALL} - Key does not exist in the JSON")
            return JsonResponse('ErrorCode#8',safe=False)
        except json.JSONDecodeError as e:
            print(f"{Fore.RED}Failed to parse JSON: {e}{Style.RESET_ALL}")
            return JsonResponse('ErrorCode#8',safe=False)
        except Exception as ex:
            print(f"{Style.RESET_ALL}Error fetching data: {ex}{Style.RESET_ALL}")
            return JsonResponse('ErrorCode#8',safe=False)

    return JsonResponse(reply_data,safe=False)



@csrf_exempt
def load_all_offers(request):
    global reply_data
    if request.method == "POST":
        try:
            jdict = json.loads(request.body)
            query="select offerid,ftitle,fdesc,fimage,epoch,date from vff.laundry_offerstbl where is_active='1'"
            if query != "":
                reply_data="ErrorCode#0"
                mapVal = execute_query_and_get_result(query)
                if mapVal != None:
                    offer_id=mapVal["1"]
                    ftitle=mapVal["2"]
                    fdesc=mapVal["3"]
                    fimage=mapVal["4"]
                    epoch_time=mapVal["5"]
                    dt=mapVal["6"]

                    offer_id_str=lst_to_str(offer_id)
                    ftitle_str=lst_to_str(ftitle)
                    fdesc_str=lst_to_str(fdesc)
                    fimage_str=lst_to_str(fimage)
                    epoch_str=lst_to_str(epoch_time)
                    date_str=lst_to_str(dt)

                    jdict={
                            "offer_id":str(offer_id_str),
                            "ftitle":str(ftitle_str),
                            "fdesc":str(fdesc_str),
                            "fimage":str(fimage_str),
                            "epoch":str(epoch_str),
                            "date":str(date_str),
                            }
                    return JsonResponse(jdict,safe=False)
        except KeyError as e:
            print(f"{Fore.RED}KeyError: {e}{Style.RESET_ALL} - Key does not exist in the JSON")
            return JsonResponse('ErrorCode#8',safe=False)
        except json.JSONDecodeError as e:
            print(f"{Fore.RED}Failed to parse JSON: {e}{Style.RESET_ALL}")
            return JsonResponse('ErrorCode#8',safe=False)
        except Exception as ex:
            print(f"{Style.RESET_ALL}Error fetching data: {ex}{Style.RESET_ALL}")
            return JsonResponse('ErrorCode#8',safe=False)

    return JsonResponse(reply_data,safe=False)

# @csrf_exempt
# def load_all_offers(request):
#     global reply_data
#     if request.method == "POST":
#         try:
#             pass
#         except KeyError as e:
#             print(f"{Fore.RED}KeyError: {e}{Style.RESET_ALL} - Key does not exist in the JSON")
#             return JsonResponse('ErrorCode#8',safe=False)
#         except json.JSONDecodeError as e:
#             print(f"{Fore.RED}Failed to parse JSON: {e}{Style.RESET_ALL}")
#             return JsonResponse('ErrorCode#8',safe=False)
#         except Exception as ex:
#             print(f"{Style.RESET_ALL}Error fetching data: {ex}{Style.RESET_ALL}")
#             return JsonResponse('ErrorCode#8',safe=False)

#     return JsonResponse('ErrorCode#8',safe=False)



