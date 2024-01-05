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

@csrf_exempt
def login(request):
    errorRet={'ErrorCode#2':'ErrorCode#2'}
    if request.method == "POST":
        # Parsing and printing JSON body
        try:
            jdict = json.loads(request.body)
            password = jdict['password']
            emailid = jdict['email_id']
            query = "select memberid,name,email,mobno,gender,weight,height,password,gymid from vff.gym_memberstbl where gym_memberstbl.email='"+str(emailid)+"' and password='"+str(password)+"'"
            result = execute_raw_query_fetch_one(query)
            if result != None:
                if result[0] != None:
                    # usrid = result[0]
                    memberid = result[0]
                    usrname = result[1]
                    emailid = result[2]
                    mobno = result[3]
                    gender = result[4]
                    weight = result[5]
                    height = result[6]
                    password = result[7]
                    gymid = result[8]
                return JsonResponse({'response': 'Success', 'email_id': emailid, 'mobno': mobno,'gender':gender,'usrname':usrname,'memberid':memberid,'weight':weight,'height':height,'gymid':gymid})
        
        except KeyError as e:
            print(f"{Fore.RED}KeyError: {e}{Style.RESET_ALL} - Key does not exist in the JSON")
            return JsonResponse({'ErrorCode#8': 'ErrorCode#8'})
        except json.JSONDecodeError as e:
            print(f"{Fore.RED}Failed to parse JSON: {e}{Style.RESET_ALL}")
            return JsonResponse({'ErrorCode#8': 'ErrorCode#8'})
        except Exception as ex:
            print(f"{Style.RESET_ALL}Error fetching data: {ex}{Style.RESET_ALL}")
            return JsonResponse({'ErrorCode#8': 'ErrorCode#8'})

    return JsonResponse(errorRet)




@csrf_exempt
def register_member(request):
    errorRet={'ErrorCode#2':'ErrorCode#2'}
    if request.method == "POST":
        # Parsing and printing JSON body
        try:
            jdict = json.loads(request.body)
            password = jdict['password']
            emailid = jdict['email_id']
            name = jdict['name']
            mobno = jdict['mobno']
            gymid = jdict['gymid']
            query = "select usertbl.usrid,memberid,usrname,gym_memberstbl.email,mobno,gym_memberstbl.gender,weight,height,password from vff.usertbl,vff.gym_memberstbl where gym_memberstbl.usrid=usertbl.usrid and gym_memberstbl.email='"+str(emailid)+"'"
            result = execute_raw_query_fetch_one(query)
            if result != None:
                return JsonResponse({'AlreadyExists':True})
            if result == None:
                try:
                    with connection.cursor() as cursor:
                        insert_query="insert into vff.usertbl(usrname,email,mobile_no) values ('"+str(name)+"','"+str(emailid)+"','"+str(mobno)+"') returning usrid"
                        cursor.execute(insert_query)
                        usrid = cursor.fetchone()[0]
                        insert_query2="insert into vff.gym_memberstbl (name,email,password,usrid,mobno,gymid) values ('"+str(name)+"','"+str(emailid)+"','"+str(password)+"','"+str(usrid)+"','"+str(mobno)+"','"+str(gymid)+"') returning memberid"
                        cursor.execute(insert_query2)
                        memberid_ret = cursor.fetchone()[0]
                        connection.commit()
                except Exception as e:
                    print(f"Error loading data: {e}")
                    return JsonResponse({'ErrorCode#8': 'ErrorCode#8'})
                
                query = "select gym_memberstbl.usrid,memberid,usrname,gym_memberstbl.email,password,mobno,gymid from vff.usertbl,vff.gym_memberstbl where gym_memberstbl.usrid=usertbl.usrid and memberid='"+str(memberid_ret)+"'"
                result = execute_raw_query_fetch_one(query)
                if result != None:
                    if result[0] != None:
                        usrid = result[0]
                        memberid = result[1]
                        usrname = result[2]
                        emailid = result[3]
                        password = result[4]
                        mobno = result[5]
                        gymid = result[6]
                    return JsonResponse({'response': 'Success', 'email_id': emailid, 'mobno': mobno,'usrid':usrid,'usrname':usrname,'memberid':memberid,'gymid':gymid})
            
        except json.JSONDecodeError as e:
            print(f"{Fore.RED}Failed to parse JSON: {e}{Style.RESET_ALL}")
            return JsonResponse({'ErrorCode#8': 'ErrorCode#8'})
        except Exception as ex:
            print(f"Error fetching data: {ex}")
            return JsonResponse({'ErrorCode#8': 'ErrorCode#8'})

    return JsonResponse(errorRet)


@csrf_exempt
def profile_complete(request):
    errorRet={'ErrorCode#2':'ErrorCode#2'}
    if request.method == "POST":
        # Parsing and printing JSON body
        try:
            jdict = json.loads(request.body)
            memberid = jdict['memberid']
            gender = jdict['gender']
            weight = jdict['weight']
            height = jdict['height']
            date_of_birth = jdict['date_of_birth']
            
            try:
                with connection.cursor() as cursor:
                    insert_query="update vff.gym_memberstbl set gender='"+str(gender)+"',weight='"+str(weight)+"',height='"+str(height)+"',date_of_birth='"+str(date_of_birth)+"' where memberid='"+str(memberid)+"'"
                    cursor.execute(insert_query)
                    connection.commit()
                    
                    return JsonResponse({'response': 'Success'})
            except Exception as e:
                print(f"Error loading data: {e}")
                return JsonResponse({'ErrorCode#8': 'ErrorCode#8'})
            
            
                
            
        except json.JSONDecodeError as e:
            print(f"{Fore.RED}Failed to parse JSON: {e}{Style.RESET_ALL}")
            return JsonResponse({'ErrorCode#8': 'ErrorCode#8'})
        except Exception as ex:
            print(f"Error fetching data: {ex}")
            return JsonResponse({'ErrorCode#8': 'ErrorCode#8'})

    return JsonResponse(errorRet)

@csrf_exempt
def set_goal(request):
    errorRet={'ErrorCode#2':'ErrorCode#2'}
    if request.method == "POST":
        # Parsing and printing JSON body
        try:
            jdict = json.loads(request.body)
            memberid = jdict['memberid']
            goal = jdict['goal']
            
            
            try:
                with connection.cursor() as cursor:
                    insert_query="update vff.gym_memberstbl set goal='"+str(goal)+"' where memberid='"+str(memberid)+"'"
                    cursor.execute(insert_query)
                    connection.commit()
                    
                    return JsonResponse({'response': 'Success'})
            except Exception as e:
                print(f"Error loading data: {e}")
                return JsonResponse({'ErrorCode#8': 'ErrorCode#8'})
            
            
                
            
        except json.JSONDecodeError as e:
            print(f"{Fore.RED}Failed to parse JSON: {e}{Style.RESET_ALL}")
            return JsonResponse({'ErrorCode#8': 'ErrorCode#8'})
        except Exception as ex:
            print(f"Error fetching data: {ex}")
            return JsonResponse({'ErrorCode#8': 'ErrorCode#8'})

    return JsonResponse(errorRet)

@csrf_exempt
def get_feesdetails(request):
    errorRet={'ErrorCode#2':'ErrorCode#2'}
    if request.method == "POST":
        # Parsing and printing JSON body
        
        try:
            jdict = json.loads(request.body)
            memberid = jdict['memberid']
            today_date = datetime.now().strftime("%Y-%m-%d")
            print(today_date)    
            query = "select memberid,name,mobno,member_type,duration_in_months,price,fees_date,last_due_date,feesid from vff.gym_feestbl,vff.gym_memberstbl where gym_feestbl.member_id=gym_memberstbl.memberid and gym_memberstbl.memberid='"+str(memberid)+"'  order by feesid desc"
            result = execute_raw_query_fetch_one(query)
            if result != None:
                if result[0] != None:
                    memberid = result[0]
                    name = result[1]
                    mobno = result[2]
                    member_type = result[3]
                    duration_in_months = result[4]
                    price = result[5]
                    fees_date = result[6]
                    last_due_date = result[7]
                    fees_id = result[8]
                    
                return JsonResponse({'response': 'Success', 'memberid': memberid, 'name': name,'mobno':mobno,'member_type':member_type,'duration_in_months':duration_in_months,'price':price,'fees_date':fees_date,'last_due_date':last_due_date,'fees_id':fees_id})
        
        except KeyError as e:
            print(f"{Fore.RED}KeyError: {e}{Style.RESET_ALL} - Key does not exist in the JSON")
            return JsonResponse({'ErrorCode#8': 'ErrorCode#8'})
        except json.JSONDecodeError as e:
            print(f"{Fore.RED}Failed to parse JSON: {e}{Style.RESET_ALL}")
            return JsonResponse({'ErrorCode#8': 'ErrorCode#8'})
        except Exception as ex:
            print(f"{Style.RESET_ALL}Error fetching data: {ex}{Style.RESET_ALL}")
            return JsonResponse({'ErrorCode#8': 'ErrorCode#8'})

    return JsonResponse(errorRet)

@csrf_exempt
def get_diet_chart_details(request):
    errorRet={'ErrorCode#2':'ErrorCode#2'}
    if request.method == "POST":
        # Parsing and printing JSON body
        
        try:
            
            today_date = datetime.now().strftime("%Y-%m-%d")
            print(today_date)    
            query = "select diet_chart_id,name,description,price,validity_in_days,image from vff.gym_main_diet_chart_tbl"
            result = execute_raw_query(query)
            data = []
            sub_items = []    
            if not result == 500:
                for row in result:
                    
                    #bookingEpoch = epochToDateTime(depoch)
                    data.append({
                    'diet_chart_id':row[0],
                    'name':row[1],
                    'description':row[2],
                    'price':row[3],
                    'validity_in_days':row[4],
                    'image':row[5]  
                    })    
            else:
                error_msg = 'Something Went Wrong'
            context ={'query_result':data} 
            return JsonResponse(context)
            
        
        except KeyError as e:
            print(f"{Fore.RED}KeyError: {e}{Style.RESET_ALL} - Key does not exist in the JSON")
            return JsonResponse({'ErrorCode#8': 'ErrorCode#8'})
        except json.JSONDecodeError as e:
            print(f"{Fore.RED}Failed to parse JSON: {e}{Style.RESET_ALL}")
            return JsonResponse({'ErrorCode#8': 'ErrorCode#8'})
        except Exception as ex:
            print(f"{Style.RESET_ALL}Error fetching data: {ex}{Style.RESET_ALL}")
            return JsonResponse({'ErrorCode#8': 'ErrorCode#8'})

    return JsonResponse(errorRet)


@csrf_exempt
def get_fees_chart_details(request):
    errorRet={'ErrorCode#2':'ErrorCode#2'}
    if request.method == "POST":
        # Parsing and printing JSON body
        
        try:
            
            today_date = datetime.now().strftime("%Y-%m-%d")
            print(today_date)    
            query = "select fdetail_id,fees_type,duration_in_months,price,description from vff.gym_fees_detailstbl"
            result = execute_raw_query(query)
            data = []
            sub_items = []    
            if not result == 500:
                for row in result:
                    
                    #bookingEpoch = epochToDateTime(depoch)
                    data.append({
                    'fdetail_id':row[0],
                    'title':row[1],
                    'duration_in_months':row[2],
                    'price':row[3],
                    'description':row[4]  
                    })    
            else:
                error_msg = 'Something Went Wrong'
            context ={'query_result':data} 
            return JsonResponse(context)
        
        except KeyError as e:
            print(f"{Fore.RED}KeyError: {e}{Style.RESET_ALL} - Key does not exist in the JSON")
            return JsonResponse({'ErrorCode#8': 'ErrorCode#8'})
        except json.JSONDecodeError as e:
            print(f"{Fore.RED}Failed to parse JSON: {e}{Style.RESET_ALL}")
            return JsonResponse({'ErrorCode#8': 'ErrorCode#8'})
        except Exception as ex:
            print(f"{Style.RESET_ALL}Error fetching data: {ex}{Style.RESET_ALL}")
            return JsonResponse({'ErrorCode#8': 'ErrorCode#8'})

    return JsonResponse(errorRet)

@csrf_exempt
def get_notification(request):
    errorRet={'ErrorCode#2':'ErrorCode#2'}
    if request.method == "POST":
        # Parsing and printing JSON body
        
        try:
            jdict = json.loads(request.body)
            memberid = jdict['memberid']
            today_date = datetime.now().strftime("%Y-%m-%d")
            
            query = "select notificationid,title,body,image,notify_date,notify_time from vff.gym_notificationtbl where member_id='"+str(memberid)+"'"
            result = execute_raw_query(query)
            data = []
            sub_items = []    
            if not result == 500:
                for row in result:
                    
                    #bookingEpoch = epochToDateTime(depoch)
                    data.append({
                    'notificationid':row[0],
                    'title':row[1],
                    'body':row[2],
                    'image':row[3],
                    'notify_date':row[4],  
                    'notify_time':row[5]   
                    })    
            else:
                error_msg = 'Something Went Wrong'
            context ={'query_result':data} 
            return JsonResponse(context)
        
        except KeyError as e:
            print(f"{Fore.RED}KeyError: {e}{Style.RESET_ALL} - Key does not exist in the JSON")
            return JsonResponse({'ErrorCode#8': 'ErrorCode#8'})
        except json.JSONDecodeError as e:
            print(f"{Fore.RED}Failed to parse JSON: {e}{Style.RESET_ALL}")
            return JsonResponse({'ErrorCode#8': 'ErrorCode#8'})
        except Exception as ex:
            print(f"{Style.RESET_ALL}Error fetching data: {ex}{Style.RESET_ALL}")
            return JsonResponse({'ErrorCode#8': 'ErrorCode#8'})

    return JsonResponse(errorRet)


@csrf_exempt
def save_gym_fees(request):
    errorRet={'ErrorCode#2':'ErrorCode#2'}
    if request.method == "POST":
        # Parsing and printing JSON body
        try:
            jdict = json.loads(request.body)
            memberid = jdict['memberid']
            amount = jdict['amount']
            recent_cleared_date = jdict['recent_cleared_date']
            duration_in_month = jdict['duration']
            payment_method = jdict['payment_method']
            razor_pay_id = jdict['razor_pay_id']
            payment_status = jdict['payment_status']
            next_due_date = jdict['next_due_date']
            
            
            try:
                with connection.cursor() as cursor:
                    # Inserting into Payment Table
                    insert_query="insert into vff.gym_paymenttbl(member_id,amount,payment_method,razor_pay_id,payment_status) values ('"+str(memberid)+"','"+str(amount)+"','"+str(payment_method)+"','"+str(razor_pay_id)+"','"+str(payment_status)+"',)"
                    cursor.execute(insert_query)
                    
                    #Inserting into Fees Table
                    fees_query_insert="insert into vff.gym_feestbl(member_type,duration_in_months,price,member_id,fees_date,last_due_date) values ('Regular Member','"+str(duration_in_month)+"','"+str(amount)+"','"+str(memberid)+"','"+str(next_due_date)+"','"+str(recent_cleared_date)+"')"
                    cursor.execute(fees_query_insert)
                    
                    connection.commit()
                    
                    return JsonResponse({'response': 'Success'})
            except Exception as e:
                print(f"Error loading data: {e}")
                return JsonResponse({'ErrorCode#8': 'ErrorCode#8'})
            
            
                
            
        except json.JSONDecodeError as e:
            print(f"{Fore.RED}Failed to parse JSON: {e}{Style.RESET_ALL}")
            return JsonResponse({'ErrorCode#8': 'ErrorCode#8'})
        except Exception as ex:
            print(f"Error fetching data: {ex}")
            return JsonResponse({'ErrorCode#8': 'ErrorCode#8'})

    return JsonResponse(errorRet)

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



def get_csrf_token(request):
    csrf_token = get_token(request)
    print(f'csrf_token_django::{csrf_token}')
    return JsonResponse({'csrf_token': csrf_token})