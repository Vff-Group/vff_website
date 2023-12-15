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
def get_main_categories(request):
    errorRet={'ErrorCode#2':'ErrorCode#2'}
    if request.method == "POST":
        # Parsing and printing JSON body
        
        try:
            
            today_date = datetime.now().strftime("%Y-%m-%d")
            
            query = "select main_cat_id,main_title_name,images from vff.united_armor_main_categorytbl"
            result = execute_raw_query(query)
            data = []
            sub_items = []    
            if not result == 500:
                for row in result:
                    
                    #bookingEpoch = epochToDateTime(depoch)
                    data.append({
                    'main_cat_id':row[0],
                    'main_title_name':row[1],
                    'images':row[2],
                    
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
def get_main_categories(request):
    errorRet={'ErrorCode#2':'ErrorCode#2'}
    if request.method == "POST":
        # Parsing and printing JSON body
        
        try:
            
            today_date = datetime.now().strftime("%Y-%m-%d")
            
            query = "select main_cat_id,main_title_name,images from vff.united_armor_main_categorytbl"
            result = execute_raw_query(query)
            data = []
            sub_items = []    
            if not result == 500:
                for row in result:
                    
                    #bookingEpoch = epochToDateTime(depoch)
                    data.append({
                    'main_cat_id':row[0],
                    'main_title_name':row[1],
                    'images':row[2],
                    
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
def get_categories(request):
    errorRet={'ErrorCode#2':'ErrorCode#2'}
    if request.method == "POST":
        # Parsing and printing JSON body
        
        try:
            jdict = json.loads(request.body)
            main_cat_id = jdict['main_cat_id']
            
            
            
            query = "select catid,cat_name from vff.united_armor_categorytbl where main_catid='"+str(main_cat_id)+"'"
            result = execute_raw_query(query)
            data = []
              
            if not result == 500:
                for row in result:
                    
                    
                    data.append({
                    'catid':row[0],
                    'cat_name':row[1],
                    
                    
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
def get_sub_categories(request):
    errorRet={'ErrorCode#2':'ErrorCode#2'}
    if request.method == "POST":
        # Parsing and printing JSON body
        
        try:
            jdict = json.loads(request.body)
            cat_id = jdict['cat_id']
            today_date = datetime.now().strftime("%Y-%m-%d")
            
            query = "select sub_catid,sub_cat_name from vff.united_armor_sub_categorytbl where catid='"+str(cat_id)+"'"
            result = execute_raw_query(query)
            data = []
            sub_items = []    
            if not result == 500:
                for row in result:
                    
                    
                    data.append({
                    'sub_catid':row[0],
                    'sub_cat_name':row[1],
                    
                    
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
def get_product_category_filter(request):
    errorRet={'ErrorCode#2':'ErrorCode#2'}
    if request.method == "POST":
        # Parsing and printing JSON body
        
        try:
            
            
            query = "select product_catid,product_category_name from vff.united_armor_product_categorytbl"
            result = execute_raw_query(query)
            data = []
            sub_items = []    
            if not result == 500:
                for row in result:
                    
                    
                    data.append({
                    'product_catid':row[0],
                    'product_category_name':row[1],
                    
                    
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
def get_product_type_filter(request):
    errorRet={'ErrorCode#2':'ErrorCode#2'}
    if request.method == "POST":
        # Parsing and printing JSON body
        
        try:
            
            
            query = "select product_type_id,product_type_name from vff.united_armor_product_typetbl"
            result = execute_raw_query(query)
            data = []
            sub_items = []    
            if not result == 500:
                for row in result:
                    
                    
                    data.append({
                    'product_type_id':row[0],
                    'product_type_name':row[1],
                    
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
def get_product_images(request):
    errorRet={'ErrorCode#2':'ErrorCode#2'}
    if request.method == "POST":
        # Parsing and printing JSON body
        
        try:
            jdict = json.loads(request.body)
            product_id = jdict['product_id']
            
            query = "select imageid,image_url from vff.united_armor_product_imagestbl where product_id='"+str(product_id)+"'"
            result = execute_raw_query(query)
            data = []
            sub_items = []    
            if not result == 500:
                for row in result:
                    
                    
                    data.append({
                    'imageid':row[0],
                    'image_url':row[1],
                    
                    
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
def get_product_colors(request):
    errorRet={'ErrorCode#2':'ErrorCode#2'}
    if request.method == "POST":
        # Parsing and printing JSON body
        
        try:
            
            jdict = json.loads(request.body)
            product_id = jdict['product_id']
            query = "select colorsid,color_name,color_code from vff.united_armor_product_colorstbl where product_id='"+str(product_id)+"'"
            result = execute_raw_query(query)
            data = []
            sub_items = []    
            if not result == 500:
                for row in result:
                    
                    
                    data.append({
                    'colorsid':row[0],
                    'color_name':row[1],
                    'color_code':row[2],
                    
                    
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

#select product_name,fitting_type,fitting_id,max_checkout_qty,what_it_does,specifications,fit_and_care_desc,main_cat_id,cat_id,sub_catid,product_collection_id,product_type_id,price from vff.united_armor_all_productstbl

#select productid,product_name,fitting_type,fitting_id,max_checkout_qty,what_it_does,specifications,fit_and_care_desc,main_title_name,cat_name,sub_cat_name,product_catid,product_category_name,united_armor_all_productstbl.product_type_id,product_type_name,price,united_armor_all_productstbl.main_cat_id,united_armor_all_productstbl.cat_id,united_armor_all_productstbl.sub_catid from vff.united_armor_all_productstbl,vff.united_armor_product_categorytbl,vff.united_armor_product_typetbl,vff.united_armor_main_categorytbl,vff.united_armor_categorytbl,vff.united_armor_sub_categorytbl where united_armor_product_categorytbl.product_catid=united_armor_all_productstbl.product_collection_id and united_armor_product_typetbl.product_type_id=united_armor_all_productstbl.product_type_id and united_armor_main_categorytbl.main_cat_id=united_armor_all_productstbl.main_cat_id and united_armor_all_productstbl.cat_id=united_armor_categorytbl.catid and united_armor_all_productstbl.sub_catid=united_armor_sub_categorytbl.sub_catid

@csrf_exempt
def load_all_product_details(request):
    errorRet={'ErrorCode#2':'ErrorCode#2'}
    if request.method == "POST":
        # Parsing and printing JSON body
        
        try:
            
            # jdict = json.loads(request.body)
            # main_cat_id = jdict['main_cat_id']
            # cat_id = jdict['cat_id']
            # sub_cat_id = jdict['sub_cat_id']
            # product_id = jdict['product_id']
            
            query = "SELECT productid,product_name,fitting_type,fitting_id,main_title_name,cat_name,sub_cat_name,product_catid,product_category_name,united_armor_all_productstbl.product_type_id,product_type_name,price,united_armor_all_productstbl.main_cat_id,united_armor_all_productstbl.cat_id,united_armor_all_productstbl.sub_catid,offer_price FROM vff.united_armor_all_productstbl,vff.united_armor_product_categorytbl,vff.united_armor_product_typetbl,vff.united_armor_main_categorytbl,vff.united_armor_categorytbl,vff.united_armor_sub_categorytbl WHERE united_armor_product_categorytbl.product_catid=united_armor_all_productstbl.product_collection_id AND united_armor_product_typetbl.product_type_id=united_armor_all_productstbl.product_type_id AND united_armor_main_categorytbl.main_cat_id=united_armor_all_productstbl.main_cat_id AND united_armor_all_productstbl.cat_id=united_armor_categorytbl.catid AND united_armor_all_productstbl.sub_catid=united_armor_sub_categorytbl.sub_catid"
            result = execute_raw_query(query)
            data = []
            sub_items = []    
            if not result == 500:
                for row in result:
                    
                    
                    data.append({
                    'productid':row[0],
                    'product_name':row[1],
                    'fitting_type':row[2],
                    'fitting_id':row[3],
                    'main_title_name':row[4],
                    'cat_name':row[5],
                    'sub_cat_name':row[6],
                    'product_catid':row[7],
                    'product_category_name':row[8],
                    'product_type_id':row[9],
                    'product_type_name':row[10],
                    'price':row[11],
                    'main_cat_id':row[12],
                    'cat_id':row[13],
                    'sub_catid':row[14],
                    
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
def load_single_product_details(request):
    errorRet={'ErrorCode#2':'ErrorCode#2'}
    if request.method == "POST":
        # Parsing and printing JSON body
        
        try:
            
            jdict = json.loads(request.body)
            # main_cat_id = jdict['main_cat_id']
            # cat_id = jdict['cat_id']
            # sub_cat_id = jdict['sub_cat_id']
            product_id = jdict['product_id']
            
            query = "SELECT product_name,fitting_type,fitting_id,max_checkout_qty,what_it_does,specifications,fit_and_care_desc,main_title_name,cat_name,sub_cat_name,product_catid,product_category_name,united_armor_all_productstbl.product_type_id,product_type_name,price,united_armor_all_productstbl.main_cat_id,united_armor_all_productstbl.cat_id,united_armor_all_productstbl.sub_catid,offer_price FROM vff.united_armor_all_productstbl,vff.united_armor_product_categorytbl,vff.united_armor_product_typetbl,vff.united_armor_main_categorytbl,vff.united_armor_categorytbl,vff.united_armor_sub_categorytbl WHERE united_armor_product_categorytbl.product_catid=united_armor_all_productstbl.product_collection_id AND united_armor_product_typetbl.product_type_id=united_armor_all_productstbl.product_type_id AND united_armor_main_categorytbl.main_cat_id=united_armor_all_productstbl.main_cat_id AND united_armor_all_productstbl.cat_id=united_armor_categorytbl.catid AND united_armor_all_productstbl.sub_catid=united_armor_sub_categorytbl.sub_catid AND productid='"+str(product_id)+"'"
            result = execute_raw_query(query)
            data = []
            sub_items = []    
            if not result == 500:
                for row in result:
                    
                    
                    data.append({
                     'product_name':row[0],
                    'fitting_type':row[1],
                    'fitting_id':row[2],
                    'max_checkout_qty':row[2],
                    'what_it_does':row[2],
                    'specifications':row[2],
                    'fit_and_care_desc':row[2],
                    'main_title_name':row[4],
                    'cat_name':row[5],
                    'sub_cat_name':row[6],
                    'product_catid':row[7],
                    'product_category_name':row[8],
                    'product_type_id':row[9],
                    'product_type_name':row[10],
                    'price':row[11],
                    'main_cat_id':row[12],
                    'cat_id':row[13],
                    'sub_catid':row[14],
                    'offer_price':row[15],
                    
                    
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






#Generic Def
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
