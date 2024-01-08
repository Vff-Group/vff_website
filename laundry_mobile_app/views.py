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
                    cursor.commit()
                    return None
                elif qtype == 1:
                    cursor.commit()
        except Exception as e:
            print(f"{Fore.RED}Query Execution Error:: {e}{Style.RESET_ALL}")
            reply_data="ErrorCode#8"
            return None
    
        recs=cursor.fetchall()
        rows=len(recs)
        print(f"{Fore.BLUE}==** Selected ROWS : {rows} **==")
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
                            cursor.commit()
                            data=cursor.fetchall()
                            if len(data) !=0:
                                rusrid=str(data[0][0])
                                print('----------Returning Usrid-----> '+str(rusrid))
                            if rusrid != "":
                                query="insert into vff.laundry_customertbl (usrid,customer_name,is_online) values ('"+str(rusrid)+"','"+str(uname)+"','1')"
                                try:
                                    cursor.execute(query)
                                    cursor.commit()
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
                                        print('jdict:: '+str(jdict))
                                        reply_data = json.dumps(jdict)
                                        # Return the data as a JSON response
                                        return JsonResponse(reply_data, safe=False)#safe because jdict is already serialized and to avoid dict confusion

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
                    reply_data = json.dumps(jdict)
                    # Return the data as a JSON response
                    return JsonResponse(reply_data, safe=False)#safe because jdict is already serialized and to avoid dict confusion
        except KeyError as e:
            print(f"{Fore.RED}KeyError: {e}{Style.RESET_ALL} - Key does not exist in the JSON")
            return JsonResponse({'ErrorCode#8': 'ErrorCode#8'})
        except json.JSONDecodeError as e:
            print(f"{Fore.RED}Failed to parse JSON: {e}{Style.RESET_ALL}")
            return JsonResponse({'ErrorCode#8': 'ErrorCode#8'})
        except Exception as ex:
            print(f"{Style.RESET_ALL}Error fetching data: {ex}{Style.RESET_ALL}")
            return JsonResponse({'ErrorCode#8': 'ErrorCode#8'})

    return JsonResponse({'ErrorCode#8': 'ErrorCode#8'})

@csrf_exempt
def load_laundry_all_categories(request):
    global reply_data 
    reply_data = {'ErrorCode#0': 'ErrorCode#0'}
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
                    reply_data=json.dumps(jdict)
                    print(f'reply_data::{reply_data}')
                    return JsonResponse(reply_data,safe=False)
        except KeyError as e:
            print(f"{Fore.RED}KeyError: {e}{Style.RESET_ALL} - Key does not exist in the JSON")
            return JsonResponse({'ErrorCode#8': 'ErrorCode#8'})
        except json.JSONDecodeError as e:
            print(f"{Fore.RED}Failed to parse JSON: {e}{Style.RESET_ALL}")
            return JsonResponse({'ErrorCode#8': 'ErrorCode#8'})
        except Exception as ex:
            print(f"{Style.RESET_ALL}Error fetching data: {ex}{Style.RESET_ALL}")
            return JsonResponse({'ErrorCode#8': 'ErrorCode#8'})

    return JsonResponse(reply_data,safe=False)


@csrf_exempt
def request_pickup_laundry_customer(request):
    global reply_data
    if request.method == "POST":
        try:
            pass
        except KeyError as e:
            print(f"{Fore.RED}KeyError: {e}{Style.RESET_ALL} - Key does not exist in the JSON")
            return JsonResponse({'ErrorCode#8': 'ErrorCode#8'})
        except json.JSONDecodeError as e:
            print(f"{Fore.RED}Failed to parse JSON: {e}{Style.RESET_ALL}")
            return JsonResponse({'ErrorCode#8': 'ErrorCode#8'})
        except Exception as ex:
            print(f"{Style.RESET_ALL}Error fetching data: {ex}{Style.RESET_ALL}")
            return JsonResponse({'ErrorCode#8': 'ErrorCode#8'})

    return JsonResponse({'ErrorCode#8': 'ErrorCode#8'})


@csrf_exempt
def update_user_device_token(request):
    global reply_data
    if request.method == "POST":
        try:
            pass
        except KeyError as e:
            print(f"{Fore.RED}KeyError: {e}{Style.RESET_ALL} - Key does not exist in the JSON")
            return JsonResponse({'ErrorCode#8': 'ErrorCode#8'})
        except json.JSONDecodeError as e:
            print(f"{Fore.RED}Failed to parse JSON: {e}{Style.RESET_ALL}")
            return JsonResponse({'ErrorCode#8': 'ErrorCode#8'})
        except Exception as ex:
            print(f"{Style.RESET_ALL}Error fetching data: {ex}{Style.RESET_ALL}")
            return JsonResponse({'ErrorCode#8': 'ErrorCode#8'})

    return JsonResponse({'ErrorCode#8': 'ErrorCode#8'})


@csrf_exempt
def delivery_boy_login(request):
    global reply_data
    if request.method == "POST":
        try:
            pass
        except KeyError as e:
            print(f"{Fore.RED}KeyError: {e}{Style.RESET_ALL} - Key does not exist in the JSON")
            return JsonResponse({'ErrorCode#8': 'ErrorCode#8'})
        except json.JSONDecodeError as e:
            print(f"{Fore.RED}Failed to parse JSON: {e}{Style.RESET_ALL}")
            return JsonResponse({'ErrorCode#8': 'ErrorCode#8'})
        except Exception as ex:
            print(f"{Style.RESET_ALL}Error fetching data: {ex}{Style.RESET_ALL}")
            return JsonResponse({'ErrorCode#8': 'ErrorCode#8'})

    return JsonResponse({'ErrorCode#8': 'ErrorCode#8'})


@csrf_exempt
#Loading Notification new orders for delivery to accept or reject the order using orderid 
def load_new_orders_requested_to_delivery_boy(request):
    global reply_data
    if request.method == "POST":
        try:
            pass
        except KeyError as e:
            print(f"{Fore.RED}KeyError: {e}{Style.RESET_ALL} - Key does not exist in the JSON")
            return JsonResponse({'ErrorCode#8': 'ErrorCode#8'})
        except json.JSONDecodeError as e:
            print(f"{Fore.RED}Failed to parse JSON: {e}{Style.RESET_ALL}")
            return JsonResponse({'ErrorCode#8': 'ErrorCode#8'})
        except Exception as ex:
            print(f"{Style.RESET_ALL}Error fetching data: {ex}{Style.RESET_ALL}")
            return JsonResponse({'ErrorCode#8': 'ErrorCode#8'})

    return JsonResponse({'ErrorCode#8': 'ErrorCode#8'})



@csrf_exempt
def accept_or_reject_order_delivery_boy(request):
    global reply_data
    if request.method == "POST":
        try:
            pass
        except KeyError as e:
            print(f"{Fore.RED}KeyError: {e}{Style.RESET_ALL} - Key does not exist in the JSON")
            return JsonResponse({'ErrorCode#8': 'ErrorCode#8'})
        except json.JSONDecodeError as e:
            print(f"{Fore.RED}Failed to parse JSON: {e}{Style.RESET_ALL}")
            return JsonResponse({'ErrorCode#8': 'ErrorCode#8'})
        except Exception as ex:
            print(f"{Style.RESET_ALL}Error fetching data: {ex}{Style.RESET_ALL}")
            return JsonResponse({'ErrorCode#8': 'ErrorCode#8'})

    return JsonResponse({'ErrorCode#8': 'ErrorCode#8'})


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
            pass
        except KeyError as e:
            print(f"{Fore.RED}KeyError: {e}{Style.RESET_ALL} - Key does not exist in the JSON")
            return JsonResponse({'ErrorCode#8': 'ErrorCode#8'})
        except json.JSONDecodeError as e:
            print(f"{Fore.RED}Failed to parse JSON: {e}{Style.RESET_ALL}")
            return JsonResponse({'ErrorCode#8': 'ErrorCode#8'})
        except Exception as ex:
            print(f"{Style.RESET_ALL}Error fetching data: {ex}{Style.RESET_ALL}")
            return JsonResponse({'ErrorCode#8': 'ErrorCode#8'})

    return JsonResponse({'ErrorCode#8': 'ErrorCode#8'})



@csrf_exempt
def send_notification_to_dashboard_without_delivery_boy(request,booking_id,senderid,mtitle,mbody,branch_id):
    global reply_data
    if request.method == "POST":
        try:
            pass
        except KeyError as e:
            print(f"{Fore.RED}KeyError: {e}{Style.RESET_ALL} - Key does not exist in the JSON")
            return JsonResponse({'ErrorCode#8': 'ErrorCode#8'})
        except json.JSONDecodeError as e:
            print(f"{Fore.RED}Failed to parse JSON: {e}{Style.RESET_ALL}")
            return JsonResponse({'ErrorCode#8': 'ErrorCode#8'})
        except Exception as ex:
            print(f"{Style.RESET_ALL}Error fetching data: {ex}{Style.RESET_ALL}")
            return JsonResponse({'ErrorCode#8': 'ErrorCode#8'})

    return JsonResponse({'ErrorCode#8': 'ErrorCode#8'})



@csrf_exempt
def send_notification_to_dashboard(request,booking_id,senderid,mtitle,mbody,mintent,mdata,branch_id,delivery_boy_id_str):
    global reply_data
    if request.method == "POST":
        try:
            pass
        except KeyError as e:
            print(f"{Fore.RED}KeyError: {e}{Style.RESET_ALL} - Key does not exist in the JSON")
            return JsonResponse({'ErrorCode#8': 'ErrorCode#8'})
        except json.JSONDecodeError as e:
            print(f"{Fore.RED}Failed to parse JSON: {e}{Style.RESET_ALL}")
            return JsonResponse({'ErrorCode#8': 'ErrorCode#8'})
        except Exception as ex:
            print(f"{Style.RESET_ALL}Error fetching data: {ex}{Style.RESET_ALL}")
            return JsonResponse({'ErrorCode#8': 'ErrorCode#8'})

    return JsonResponse({'ErrorCode#8': 'ErrorCode#8'})



@csrf_exempt
def send_notification_to_delivery_boy(request,booking_id,senderid,mtitle,mbody,mintent,mdata,branch_id):
    global reply_data
    if request.method == "POST":
        try:
            pass
        except KeyError as e:
            print(f"{Fore.RED}KeyError: {e}{Style.RESET_ALL} - Key does not exist in the JSON")
            return JsonResponse({'ErrorCode#8': 'ErrorCode#8'})
        except json.JSONDecodeError as e:
            print(f"{Fore.RED}Failed to parse JSON: {e}{Style.RESET_ALL}")
            return JsonResponse({'ErrorCode#8': 'ErrorCode#8'})
        except Exception as ex:
            print(f"{Style.RESET_ALL}Error fetching data: {ex}{Style.RESET_ALL}")
            return JsonResponse({'ErrorCode#8': 'ErrorCode#8'})

    return JsonResponse({'ErrorCode#8': 'ErrorCode#8'})


'''
To Update order status at every stage of order
'''
@csrf_exempt
def update_order_status(request,order_id,status):
    global reply_data
    if request.method == "POST":
        try:
            pass
        except KeyError as e:
            print(f"{Fore.RED}KeyError: {e}{Style.RESET_ALL} - Key does not exist in the JSON")
            return JsonResponse({'ErrorCode#8': 'ErrorCode#8'})
        except json.JSONDecodeError as e:
            print(f"{Fore.RED}Failed to parse JSON: {e}{Style.RESET_ALL}")
            return JsonResponse({'ErrorCode#8': 'ErrorCode#8'})
        except Exception as ex:
            print(f"{Style.RESET_ALL}Error fetching data: {ex}{Style.RESET_ALL}")
            return JsonResponse({'ErrorCode#8': 'ErrorCode#8'})

    return JsonResponse({'ErrorCode#8': 'ErrorCode#8'})



@csrf_exempt
def update_booking_status(request,booking_id,status):
    global reply_data
    if request.method == "POST":
        try:
            pass
        except KeyError as e:
            print(f"{Fore.RED}KeyError: {e}{Style.RESET_ALL} - Key does not exist in the JSON")
            return JsonResponse({'ErrorCode#8': 'ErrorCode#8'})
        except json.JSONDecodeError as e:
            print(f"{Fore.RED}Failed to parse JSON: {e}{Style.RESET_ALL}")
            return JsonResponse({'ErrorCode#8': 'ErrorCode#8'})
        except Exception as ex:
            print(f"{Style.RESET_ALL}Error fetching data: {ex}{Style.RESET_ALL}")
            return JsonResponse({'ErrorCode#8': 'ErrorCode#8'})

    return JsonResponse({'ErrorCode#8': 'ErrorCode#8'})


'''
Active Order Details for customer
'''
@csrf_exempt
def load_customer_active_order_details(request):
    global reply_data
    if request.method == "POST":
        try:
            pass
        except KeyError as e:
            print(f"{Fore.RED}KeyError: {e}{Style.RESET_ALL} - Key does not exist in the JSON")
            return JsonResponse({'ErrorCode#8': 'ErrorCode#8'})
        except json.JSONDecodeError as e:
            print(f"{Fore.RED}Failed to parse JSON: {e}{Style.RESET_ALL}")
            return JsonResponse({'ErrorCode#8': 'ErrorCode#8'})
        except Exception as ex:
            print(f"{Style.RESET_ALL}Error fetching data: {ex}{Style.RESET_ALL}")
            return JsonResponse({'ErrorCode#8': 'ErrorCode#8'})

    return JsonResponse({'ErrorCode#8': 'ErrorCode#8'})



@csrf_exempt
def load_selected_order_items_order_detail(request):
    global reply_data
    if request.method == "POST":
        try:
            pass
        except KeyError as e:
            print(f"{Fore.RED}KeyError: {e}{Style.RESET_ALL} - Key does not exist in the JSON")
            return JsonResponse({'ErrorCode#8': 'ErrorCode#8'})
        except json.JSONDecodeError as e:
            print(f"{Fore.RED}Failed to parse JSON: {e}{Style.RESET_ALL}")
            return JsonResponse({'ErrorCode#8': 'ErrorCode#8'})
        except Exception as ex:
            print(f"{Style.RESET_ALL}Error fetching data: {ex}{Style.RESET_ALL}")
            return JsonResponse({'ErrorCode#8': 'ErrorCode#8'})

    return JsonResponse({'ErrorCode#8': 'ErrorCode#8'})



@csrf_exempt
def load_category_wise_details(request):
    global reply_data
    if request.method == "POST":
        try:
            pass
        except KeyError as e:
            print(f"{Fore.RED}KeyError: {e}{Style.RESET_ALL} - Key does not exist in the JSON")
            return JsonResponse({'ErrorCode#8': 'ErrorCode#8'})
        except json.JSONDecodeError as e:
            print(f"{Fore.RED}Failed to parse JSON: {e}{Style.RESET_ALL}")
            return JsonResponse({'ErrorCode#8': 'ErrorCode#8'})
        except Exception as ex:
            print(f"{Style.RESET_ALL}Error fetching data: {ex}{Style.RESET_ALL}")
            return JsonResponse({'ErrorCode#8': 'ErrorCode#8'})

    return JsonResponse({'ErrorCode#8': 'ErrorCode#8'})



@csrf_exempt
def load_sub_category_wise_details(request):
    global reply_data
    if request.method == "POST":
        try:
            pass
        except KeyError as e:
            print(f"{Fore.RED}KeyError: {e}{Style.RESET_ALL} - Key does not exist in the JSON")
            return JsonResponse({'ErrorCode#8': 'ErrorCode#8'})
        except json.JSONDecodeError as e:
            print(f"{Fore.RED}Failed to parse JSON: {e}{Style.RESET_ALL}")
            return JsonResponse({'ErrorCode#8': 'ErrorCode#8'})
        except Exception as ex:
            print(f"{Style.RESET_ALL}Error fetching data: {ex}{Style.RESET_ALL}")
            return JsonResponse({'ErrorCode#8': 'ErrorCode#8'})

    return JsonResponse({'ErrorCode#8': 'ErrorCode#8'})



@csrf_exempt
def load_sub_category_section_wise_details(request):
    global reply_data
    if request.method == "POST":
        try:
            pass
        except KeyError as e:
            print(f"{Fore.RED}KeyError: {e}{Style.RESET_ALL} - Key does not exist in the JSON")
            return JsonResponse({'ErrorCode#8': 'ErrorCode#8'})
        except json.JSONDecodeError as e:
            print(f"{Fore.RED}Failed to parse JSON: {e}{Style.RESET_ALL}")
            return JsonResponse({'ErrorCode#8': 'ErrorCode#8'})
        except Exception as ex:
            print(f"{Style.RESET_ALL}Error fetching data: {ex}{Style.RESET_ALL}")
            return JsonResponse({'ErrorCode#8': 'ErrorCode#8'})

    return JsonResponse({'ErrorCode#8': 'ErrorCode#8'})



@csrf_exempt
def add_laundry_items_to_cart(request):
    global reply_data
    if request.method == "POST":
        try:
            pass
        except KeyError as e:
            print(f"{Fore.RED}KeyError: {e}{Style.RESET_ALL} - Key does not exist in the JSON")
            return JsonResponse({'ErrorCode#8': 'ErrorCode#8'})
        except json.JSONDecodeError as e:
            print(f"{Fore.RED}Failed to parse JSON: {e}{Style.RESET_ALL}")
            return JsonResponse({'ErrorCode#8': 'ErrorCode#8'})
        except Exception as ex:
            print(f"{Style.RESET_ALL}Error fetching data: {ex}{Style.RESET_ALL}")
            return JsonResponse({'ErrorCode#8': 'ErrorCode#8'})

    return JsonResponse({'ErrorCode#8': 'ErrorCode#8'})



@csrf_exempt
def delete_laundry_cart_item(request):
    global reply_data
    if request.method == "POST":
        try:
            pass
        except KeyError as e:
            print(f"{Fore.RED}KeyError: {e}{Style.RESET_ALL} - Key does not exist in the JSON")
            return JsonResponse({'ErrorCode#8': 'ErrorCode#8'})
        except json.JSONDecodeError as e:
            print(f"{Fore.RED}Failed to parse JSON: {e}{Style.RESET_ALL}")
            return JsonResponse({'ErrorCode#8': 'ErrorCode#8'})
        except Exception as ex:
            print(f"{Style.RESET_ALL}Error fetching data: {ex}{Style.RESET_ALL}")
            return JsonResponse({'ErrorCode#8': 'ErrorCode#8'})

    return JsonResponse({'ErrorCode#8': 'ErrorCode#8'})



@csrf_exempt
def load_cart_items_selected(request):
    global reply_data
    if request.method == "POST":
        try:
            pass
        except KeyError as e:
            print(f"{Fore.RED}KeyError: {e}{Style.RESET_ALL} - Key does not exist in the JSON")
            return JsonResponse({'ErrorCode#8': 'ErrorCode#8'})
        except json.JSONDecodeError as e:
            print(f"{Fore.RED}Failed to parse JSON: {e}{Style.RESET_ALL}")
            return JsonResponse({'ErrorCode#8': 'ErrorCode#8'})
        except Exception as ex:
            print(f"{Style.RESET_ALL}Error fetching data: {ex}{Style.RESET_ALL}")
            return JsonResponse({'ErrorCode#8': 'ErrorCode#8'})

    return JsonResponse({'ErrorCode#8': 'ErrorCode#8'})



@csrf_exempt
def load_extra_items_details(request):
    global reply_data
    if request.method == "POST":
        try:
            pass
        except KeyError as e:
            print(f"{Fore.RED}KeyError: {e}{Style.RESET_ALL} - Key does not exist in the JSON")
            return JsonResponse({'ErrorCode#8': 'ErrorCode#8'})
        except json.JSONDecodeError as e:
            print(f"{Fore.RED}Failed to parse JSON: {e}{Style.RESET_ALL}")
            return JsonResponse({'ErrorCode#8': 'ErrorCode#8'})
        except Exception as ex:
            print(f"{Style.RESET_ALL}Error fetching data: {ex}{Style.RESET_ALL}")
            return JsonResponse({'ErrorCode#8': 'ErrorCode#8'})

    return JsonResponse({'ErrorCode#8': 'ErrorCode#8'})


@csrf_exempt
def place_order_laundry(request):
    global reply_data
    if request.method == "POST":
        try:
            pass
        except KeyError as e:
            print(f"{Fore.RED}KeyError: {e}{Style.RESET_ALL} - Key does not exist in the JSON")
            return JsonResponse({'ErrorCode#8': 'ErrorCode#8'})
        except json.JSONDecodeError as e:
            print(f"{Fore.RED}Failed to parse JSON: {e}{Style.RESET_ALL}")
            return JsonResponse({'ErrorCode#8': 'ErrorCode#8'})
        except Exception as ex:
            print(f"{Style.RESET_ALL}Error fetching data: {ex}{Style.RESET_ALL}")
            return JsonResponse({'ErrorCode#8': 'ErrorCode#8'})

    return JsonResponse({'ErrorCode#8': 'ErrorCode#8'})



@csrf_exempt
def cancel_laundry_order(request):
    global reply_data
    if request.method == "POST":
        try:
            pass
        except KeyError as e:
            print(f"{Fore.RED}KeyError: {e}{Style.RESET_ALL} - Key does not exist in the JSON")
            return JsonResponse({'ErrorCode#8': 'ErrorCode#8'})
        except json.JSONDecodeError as e:
            print(f"{Fore.RED}Failed to parse JSON: {e}{Style.RESET_ALL}")
            return JsonResponse({'ErrorCode#8': 'ErrorCode#8'})
        except Exception as ex:
            print(f"{Style.RESET_ALL}Error fetching data: {ex}{Style.RESET_ALL}")
            return JsonResponse({'ErrorCode#8': 'ErrorCode#8'})

    return JsonResponse({'ErrorCode#8': 'ErrorCode#8'})



@csrf_exempt
def feedback_laundry_order(request):
    global reply_data
    if request.method == "POST":
        try:
            pass
        except KeyError as e:
            print(f"{Fore.RED}KeyError: {e}{Style.RESET_ALL} - Key does not exist in the JSON")
            return JsonResponse({'ErrorCode#8': 'ErrorCode#8'})
        except json.JSONDecodeError as e:
            print(f"{Fore.RED}Failed to parse JSON: {e}{Style.RESET_ALL}")
            return JsonResponse({'ErrorCode#8': 'ErrorCode#8'})
        except Exception as ex:
            print(f"{Style.RESET_ALL}Error fetching data: {ex}{Style.RESET_ALL}")
            return JsonResponse({'ErrorCode#8': 'ErrorCode#8'})

    return JsonResponse({'ErrorCode#8': 'ErrorCode#8'})



@csrf_exempt
def mark_delivery_boy_as_online(request):
    global reply_data
    if request.method == "POST":
        try:
            pass
        except KeyError as e:
            print(f"{Fore.RED}KeyError: {e}{Style.RESET_ALL} - Key does not exist in the JSON")
            return JsonResponse({'ErrorCode#8': 'ErrorCode#8'})
        except json.JSONDecodeError as e:
            print(f"{Fore.RED}Failed to parse JSON: {e}{Style.RESET_ALL}")
            return JsonResponse({'ErrorCode#8': 'ErrorCode#8'})
        except Exception as ex:
            print(f"{Style.RESET_ALL}Error fetching data: {ex}{Style.RESET_ALL}")
            return JsonResponse({'ErrorCode#8': 'ErrorCode#8'})

    return JsonResponse({'ErrorCode#8': 'ErrorCode#8'})



@csrf_exempt
def load_all_orders_tab_details(request):
    global reply_data
    if request.method == "POST":
        try:
            pass
        except KeyError as e:
            print(f"{Fore.RED}KeyError: {e}{Style.RESET_ALL} - Key does not exist in the JSON")
            return JsonResponse({'ErrorCode#8': 'ErrorCode#8'})
        except json.JSONDecodeError as e:
            print(f"{Fore.RED}Failed to parse JSON: {e}{Style.RESET_ALL}")
            return JsonResponse({'ErrorCode#8': 'ErrorCode#8'})
        except Exception as ex:
            print(f"{Style.RESET_ALL}Error fetching data: {ex}{Style.RESET_ALL}")
            return JsonResponse({'ErrorCode#8': 'ErrorCode#8'})

    return JsonResponse({'ErrorCode#8': 'ErrorCode#8'})



@csrf_exempt
def load_delivery_boy_all_orders_tab_details(request):
    global reply_data
    if request.method == "POST":
        try:
            pass
        except KeyError as e:
            print(f"{Fore.RED}KeyError: {e}{Style.RESET_ALL} - Key does not exist in the JSON")
            return JsonResponse({'ErrorCode#8': 'ErrorCode#8'})
        except json.JSONDecodeError as e:
            print(f"{Fore.RED}Failed to parse JSON: {e}{Style.RESET_ALL}")
            return JsonResponse({'ErrorCode#8': 'ErrorCode#8'})
        except Exception as ex:
            print(f"{Style.RESET_ALL}Error fetching data: {ex}{Style.RESET_ALL}")
            return JsonResponse({'ErrorCode#8': 'ErrorCode#8'})

    return JsonResponse({'ErrorCode#8': 'ErrorCode#8'})



@csrf_exempt
def delivery_boycurrent_active_order_details(request):
    global reply_data
    if request.method == "POST":
        try:
            pass
        except KeyError as e:
            print(f"{Fore.RED}KeyError: {e}{Style.RESET_ALL} - Key does not exist in the JSON")
            return JsonResponse({'ErrorCode#8': 'ErrorCode#8'})
        except json.JSONDecodeError as e:
            print(f"{Fore.RED}Failed to parse JSON: {e}{Style.RESET_ALL}")
            return JsonResponse({'ErrorCode#8': 'ErrorCode#8'})
        except Exception as ex:
            print(f"{Style.RESET_ALL}Error fetching data: {ex}{Style.RESET_ALL}")
            return JsonResponse({'ErrorCode#8': 'ErrorCode#8'})

    return JsonResponse({'ErrorCode#8': 'ErrorCode#8'})



@csrf_exempt
def send_notification_to_assigned_delivery_boy_for_booking(request,sender_id,mtitle,mbody,mintent,bookingid,mdata):
    global reply_data
    if request.method == "POST":
        try:
            pass
        except KeyError as e:
            print(f"{Fore.RED}KeyError: {e}{Style.RESET_ALL} - Key does not exist in the JSON")
            return JsonResponse({'ErrorCode#8': 'ErrorCode#8'})
        except json.JSONDecodeError as e:
            print(f"{Fore.RED}Failed to parse JSON: {e}{Style.RESET_ALL}")
            return JsonResponse({'ErrorCode#8': 'ErrorCode#8'})
        except Exception as ex:
            print(f"{Style.RESET_ALL}Error fetching data: {ex}{Style.RESET_ALL}")
            return JsonResponse({'ErrorCode#8': 'ErrorCode#8'})

    return JsonResponse({'ErrorCode#8': 'ErrorCode#8'})



@csrf_exempt
def send_notification_to_assigned_delivery_boy(request,sender_id,mtitle,mbody,mintent,orderid,mdata):
    global reply_data
    if request.method == "POST":
        try:
            pass
        except KeyError as e:
            print(f"{Fore.RED}KeyError: {e}{Style.RESET_ALL} - Key does not exist in the JSON")
            return JsonResponse({'ErrorCode#8': 'ErrorCode#8'})
        except json.JSONDecodeError as e:
            print(f"{Fore.RED}Failed to parse JSON: {e}{Style.RESET_ALL}")
            return JsonResponse({'ErrorCode#8': 'ErrorCode#8'})
        except Exception as ex:
            print(f"{Style.RESET_ALL}Error fetching data: {ex}{Style.RESET_ALL}")
            return JsonResponse({'ErrorCode#8': 'ErrorCode#8'})

    return JsonResponse({'ErrorCode#8': 'ErrorCode#8'})



@csrf_exempt
def send_notification_to_customer_with_bookingid(request,sender_id,mtitle,mbody,mintent,booking_id,mdata):
    global reply_data
    if request.method == "POST":
        try:
            pass
        except KeyError as e:
            print(f"{Fore.RED}KeyError: {e}{Style.RESET_ALL} - Key does not exist in the JSON")
            return JsonResponse({'ErrorCode#8': 'ErrorCode#8'})
        except json.JSONDecodeError as e:
            print(f"{Fore.RED}Failed to parse JSON: {e}{Style.RESET_ALL}")
            return JsonResponse({'ErrorCode#8': 'ErrorCode#8'})
        except Exception as ex:
            print(f"{Style.RESET_ALL}Error fetching data: {ex}{Style.RESET_ALL}")
            return JsonResponse({'ErrorCode#8': 'ErrorCode#8'})

    return JsonResponse({'ErrorCode#8': 'ErrorCode#8'})



@csrf_exempt
def send_notification_to_customer(request,sender_id,mtitle,mbody,mintent,orderid,mdata):
    global reply_data
    if request.method == "POST":
        try:
            pass
        except KeyError as e:
            print(f"{Fore.RED}KeyError: {e}{Style.RESET_ALL} - Key does not exist in the JSON")
            return JsonResponse({'ErrorCode#8': 'ErrorCode#8'})
        except json.JSONDecodeError as e:
            print(f"{Fore.RED}Failed to parse JSON: {e}{Style.RESET_ALL}")
            return JsonResponse({'ErrorCode#8': 'ErrorCode#8'})
        except Exception as ex:
            print(f"{Style.RESET_ALL}Error fetching data: {ex}{Style.RESET_ALL}")
            return JsonResponse({'ErrorCode#8': 'ErrorCode#8'})

    return JsonResponse({'ErrorCode#8': 'ErrorCode#8'})



@csrf_exempt
def update_current_order_status(request):
    global reply_data
    if request.method == "POST":
        try:
            pass
        except KeyError as e:
            print(f"{Fore.RED}KeyError: {e}{Style.RESET_ALL} - Key does not exist in the JSON")
            return JsonResponse({'ErrorCode#8': 'ErrorCode#8'})
        except json.JSONDecodeError as e:
            print(f"{Fore.RED}Failed to parse JSON: {e}{Style.RESET_ALL}")
            return JsonResponse({'ErrorCode#8': 'ErrorCode#8'})
        except Exception as ex:
            print(f"{Style.RESET_ALL}Error fetching data: {ex}{Style.RESET_ALL}")
            return JsonResponse({'ErrorCode#8': 'ErrorCode#8'})

    return JsonResponse({'ErrorCode#8': 'ErrorCode#8'})



@csrf_exempt
def update_current_new_booking_status(request):
    global reply_data
    if request.method == "POST":
        try:
            pass
        except KeyError as e:
            print(f"{Fore.RED}KeyError: {e}{Style.RESET_ALL} - Key does not exist in the JSON")
            return JsonResponse({'ErrorCode#8': 'ErrorCode#8'})
        except json.JSONDecodeError as e:
            print(f"{Fore.RED}Failed to parse JSON: {e}{Style.RESET_ALL}")
            return JsonResponse({'ErrorCode#8': 'ErrorCode#8'})
        except Exception as ex:
            print(f"{Style.RESET_ALL}Error fetching data: {ex}{Style.RESET_ALL}")
            return JsonResponse({'ErrorCode#8': 'ErrorCode#8'})

    return JsonResponse({'ErrorCode#8': 'ErrorCode#8'})




@csrf_exempt
def load_todays_notifications(request):
    global reply_data
    if request.method == "POST":
        try:
            pass
        except KeyError as e:
            print(f"{Fore.RED}KeyError: {e}{Style.RESET_ALL} - Key does not exist in the JSON")
            return JsonResponse({'ErrorCode#8': 'ErrorCode#8'})
        except json.JSONDecodeError as e:
            print(f"{Fore.RED}Failed to parse JSON: {e}{Style.RESET_ALL}")
            return JsonResponse({'ErrorCode#8': 'ErrorCode#8'})
        except Exception as ex:
            print(f"{Style.RESET_ALL}Error fetching data: {ex}{Style.RESET_ALL}")
            return JsonResponse({'ErrorCode#8': 'ErrorCode#8'})

    return JsonResponse({'ErrorCode#8': 'ErrorCode#8'})



@csrf_exempt
def delivery_boy_stats(request):
    global reply_data
    if request.method == "POST":
        try:
            pass
        except KeyError as e:
            print(f"{Fore.RED}KeyError: {e}{Style.RESET_ALL} - Key does not exist in the JSON")
            return JsonResponse({'ErrorCode#8': 'ErrorCode#8'})
        except json.JSONDecodeError as e:
            print(f"{Fore.RED}Failed to parse JSON: {e}{Style.RESET_ALL}")
            return JsonResponse({'ErrorCode#8': 'ErrorCode#8'})
        except Exception as ex:
            print(f"{Style.RESET_ALL}Error fetching data: {ex}{Style.RESET_ALL}")
            return JsonResponse({'ErrorCode#8': 'ErrorCode#8'})

    return JsonResponse({'ErrorCode#8': 'ErrorCode#8'})



@csrf_exempt
def load_all_branches(request):
    global reply_data
    if request.method == "POST":
        try:
            pass
        except KeyError as e:
            print(f"{Fore.RED}KeyError: {e}{Style.RESET_ALL} - Key does not exist in the JSON")
            return JsonResponse({'ErrorCode#8': 'ErrorCode#8'})
        except json.JSONDecodeError as e:
            print(f"{Fore.RED}Failed to parse JSON: {e}{Style.RESET_ALL}")
            return JsonResponse({'ErrorCode#8': 'ErrorCode#8'})
        except Exception as ex:
            print(f"{Style.RESET_ALL}Error fetching data: {ex}{Style.RESET_ALL}")
            return JsonResponse({'ErrorCode#8': 'ErrorCode#8'})

    return JsonResponse({'ErrorCode#8': 'ErrorCode#8'})




@csrf_exempt
def load_all_pickup_order(request):
    global reply_data
    if request.method == "POST":
        try:
            pass
        except KeyError as e:
            print(f"{Fore.RED}KeyError: {e}{Style.RESET_ALL} - Key does not exist in the JSON")
            return JsonResponse({'ErrorCode#8': 'ErrorCode#8'})
        except json.JSONDecodeError as e:
            print(f"{Fore.RED}Failed to parse JSON: {e}{Style.RESET_ALL}")
            return JsonResponse({'ErrorCode#8': 'ErrorCode#8'})
        except Exception as ex:
            print(f"{Style.RESET_ALL}Error fetching data: {ex}{Style.RESET_ALL}")
            return JsonResponse({'ErrorCode#8': 'ErrorCode#8'})

    return JsonResponse({'ErrorCode#8': 'ErrorCode#8'})




@csrf_exempt
def load_all_drop_order(request):
    global reply_data
    if request.method == "POST":
        try:
            pass
        except KeyError as e:
            print(f"{Fore.RED}KeyError: {e}{Style.RESET_ALL} - Key does not exist in the JSON")
            return JsonResponse({'ErrorCode#8': 'ErrorCode#8'})
        except json.JSONDecodeError as e:
            print(f"{Fore.RED}Failed to parse JSON: {e}{Style.RESET_ALL}")
            return JsonResponse({'ErrorCode#8': 'ErrorCode#8'})
        except Exception as ex:
            print(f"{Style.RESET_ALL}Error fetching data: {ex}{Style.RESET_ALL}")
            return JsonResponse({'ErrorCode#8': 'ErrorCode#8'})

    return JsonResponse({'ErrorCode#8': 'ErrorCode#8'})


@csrf_exempt
def load_all_pickup_or_drop_booking_details(request):
    global reply_data
    if request.method == "POST":
        try:
            pass
        except KeyError as e:
            print(f"{Fore.RED}KeyError: {e}{Style.RESET_ALL} - Key does not exist in the JSON")
            return JsonResponse({'ErrorCode#8': 'ErrorCode#8'})
        except json.JSONDecodeError as e:
            print(f"{Fore.RED}Failed to parse JSON: {e}{Style.RESET_ALL}")
            return JsonResponse({'ErrorCode#8': 'ErrorCode#8'})
        except Exception as ex:
            print(f"{Style.RESET_ALL}Error fetching data: {ex}{Style.RESET_ALL}")
            return JsonResponse({'ErrorCode#8': 'ErrorCode#8'})

    return JsonResponse({'ErrorCode#8': 'ErrorCode#8'})





@csrf_exempt
def load_all_offers(request):
    global reply_data
    if request.method == "POST":
        try:
            pass
        except KeyError as e:
            print(f"{Fore.RED}KeyError: {e}{Style.RESET_ALL} - Key does not exist in the JSON")
            return JsonResponse({'ErrorCode#8': 'ErrorCode#8'})
        except json.JSONDecodeError as e:
            print(f"{Fore.RED}Failed to parse JSON: {e}{Style.RESET_ALL}")
            return JsonResponse({'ErrorCode#8': 'ErrorCode#8'})
        except Exception as ex:
            print(f"{Style.RESET_ALL}Error fetching data: {ex}{Style.RESET_ALL}")
            return JsonResponse({'ErrorCode#8': 'ErrorCode#8'})

    return JsonResponse({'ErrorCode#8': 'ErrorCode#8'})



