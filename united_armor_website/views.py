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
from django.views.decorators.cache import cache_page
from django.contrib.sessions.models import Session


from PIL import Image  # Pillow library for image processing

# Create your views here.
#Coming Soon Page
def coming_soon(request):
    current_url = request.get_full_path()
    return render(request,"coming_soon.html",{'current_url': current_url})

def handle_login(request):
    if request.method == 'POST':
        username = request.POST.get('singin-email')
        password = request.POST.get('singin-password')

        # Perform your login logic here
        query = "select customerid,customer_name from vff.united_armor_customertbl where email='"+str(username)+"' and password='"+str(password)+"'"
        user_data = execute_raw_query_fetch_one(query)
        if user_data :
                # User is authorized
                print('User is Authorized')
                request.session['u_customer_id'] = user_data[0]
                request.session['customer_name'] = user_data[1]
                return JsonResponse({'message': 'Login successful'})        
        else:
            error_msg = 'Something Went Wrong'
            return JsonResponse({'message': 'InValid Login Credentials'})
        
        
    else:
        # Handle other HTTP methods if needed
        return JsonResponse({'message': 'Invalid request method'})
    
#Home Page
@cache_page(60 * 15)  # Cache for 15 minutes
def home(request):
    main_cat_query = "SELECT main_cat_id, main_title_name,images FROM vff.united_armor_main_categorytbl ORDER BY main_cat_id"
    main_cat_result = execute_raw_query(main_cat_query)

    all_categories = []
    if not main_cat_result == 500:
        for main_cat_row in main_cat_result:
            main_cat_id = main_cat_row[0]
            main_cat_name = main_cat_row[1]
            main_image = main_cat_row[2]

            cat_query = f"SELECT catid, cat_name FROM vff.united_armor_categorytbl WHERE main_catid = {main_cat_id} ORDER BY catid"
            cat_result = execute_raw_query(cat_query)

            sub_categories = []
            if cat_result and len(cat_result) > 0:
                for cat_row in cat_result:
                    cat_id = cat_row[0]
                    cat_name = cat_row[1]

                    sub_cat_query = f"SELECT sub_catid, sub_cat_name FROM vff.united_armor_sub_categorytbl WHERE catid = {cat_id} ORDER BY sub_catid"
                    sub_cat_result = execute_raw_query(sub_cat_query)

                    sub_cat_data = []
                    if sub_cat_result and len(sub_cat_result) > 0: 
                        for sub_cat_row in sub_cat_result:
                            sub_catid = sub_cat_row[0]
                            sub_cat_name = sub_cat_row[1]
                            
                            sub_cat_data.append({
                                'sub_cat_id': sub_catid,
                                'sub_cat_name': sub_cat_name,
                            })
                            # print(f'sub_cat_name::{sub_cat_name}')

                    cat_data = {
                        'cat_id': cat_id,
                        'cat_name': cat_name,
                        'sub_category': sub_cat_data,
                    }
                    sub_categories.append(cat_data)

            main_cat_data = {
                'main_cat_id': main_cat_id,
                'main_cat_name': main_cat_name,
                'images':main_image,
                'categories': sub_categories,
            }
            all_categories.append(main_cat_data)
    else:
        error_msg = 'Something Went Wrong'

    current_url = request.get_full_path()
    context = {'all_categories': all_categories, 'current_url': current_url}
    return render(request, "home_pages/home.html", context)


# def home(request):
#     query = "SELECT main_cat_id, main_title_name, images FROM vff.united_armor_main_categorytbl ORDER BY main_cat_id"
#     query_result = execute_raw_query(query)

#     main_cat_data = []    
#     if not query_result == 500:
#         for row in query_result:
#             main_cat_id = row[0]

#             # Nested query to select catid and cat_name where main_catid is unique
#             cat_query = f"SELECT catid, cat_name FROM vff.united_armor_categorytbl WHERE main_catid = {main_cat_id} order by catid"
#             cat_result = execute_raw_query(cat_query)

#             # Nested query to select sub_catid and sub_cat_name where catid is unique
#             if cat_result and len(cat_result) > 0:
#                 catid = cat_result[0][0]
#                 sub_cat_query = f"SELECT sub_catid, sub_cat_name FROM vff.united_armor_sub_categorytbl WHERE catid = {catid} order by sub_catid"
#                 sub_cat_result = execute_raw_query(sub_cat_query)

#                 if sub_cat_result and len(sub_cat_result) > 0:
#                     sub_cat_data = {
#                         'sub_catid': sub_cat_result[0][0],
#                         'sub_cat_name': sub_cat_result[0][1],
#                     }
#                 else:
#                     # Handle the case when no matching entry is found in united_armor_sub_categorytbl
#                     sub_cat_data = {
#                         'sub_catid': None,
#                         'sub_cat_name': None,
#                     }

#                 cat_data = {
#                     'main_cat_id': main_cat_id,
#                     'main_title_name': row[1],
#                     'images': row[2],
#                     'catid': catid,
#                     'cat_name': cat_result[0][1],
#                     'sub_category': sub_cat_data,
#                 }
#                 main_cat_data.append(cat_data)
#             else:
#                 # Handle the case when no matching entry is found in united_armor_categorytbl
#                 main_cat_data.append({
#                     'main_cat_id': main_cat_id,
#                     'main_title_name': row[1],
#                     'images': row[2],
#                     'catid': None,
#                     'cat_name': None,
#                     'sub_category': {
#                         'sub_catid': None,
#                         'sub_cat_name': None,
#                     },
#                 })
#     else:
#         error_msg = 'Something Went Wrong'

    
#     current_url = request.get_full_path()
#     context={'main_cat_data':main_cat_data,'current_url': current_url}
#     return render(request,"home_pages/home.html",context)

# def home(request):
#     query = "SELECT main_cat_id, main_title_name, images FROM vff.united_armor_main_categorytbl ORDER BY main_cat_id"
#     query_result = execute_raw_query(query)

#     main_cat_data = []
#     all_cat_names = []  # List to store all cat_names
#     all_sub_cat_names = []  # List to store all sub_cat_names

#     if not query_result == 500:
#         for row in query_result:
#             main_cat_id = row[0]

#             # Nested query to select catid and cat_name where main_catid is unique
#             cat_query = f"SELECT catid, cat_name FROM vff.united_armor_categorytbl WHERE main_catid = {main_cat_id} order by catid"
#             cat_result = execute_raw_query(cat_query)

#             # Nested query to select sub_catid and sub_cat_name where catid is unique
#             if cat_result and len(cat_result) > 0:
#                 catid = cat_result[0][0]
#                 sub_cat_query = f"SELECT sub_catid, sub_cat_name FROM vff.united_armor_sub_categorytbl WHERE catid = {catid} order by sub_catid"
#                 sub_cat_result = execute_raw_query(sub_cat_query)

#                 if sub_cat_result and len(sub_cat_result) > 0:
#                     sub_cat_data = {
#                         'sub_catid': sub_cat_result[0][0],
#                         'sub_cat_name': sub_cat_result[0][1],
#                     }

#                     # Append sub_cat_name to the list
#                     all_sub_cat_names.append(sub_cat_result[0][1])
#                 else:
#                     # Handle the case when no matching entry is found in united_armor_sub_categorytbl
#                     sub_cat_data = {
#                         'sub_catid': None,
#                         'sub_cat_name': None,
#                     }

#                 # Append cat_name to the list
#                 all_cat_names.append(cat_result[0][1])

#                 cat_data = {
#                     'main_cat_id': main_cat_id,
#                     'main_title_name': row[1],
#                     'images': row[2],
#                     'catid': catid,
#                     'cat_name': cat_result[0][1],
#                     'sub_category': sub_cat_data,
#                 }
#                 main_cat_data.append(cat_data)
#             else:
#                 # Handle the case when no matching entry is found in united_armor_categorytbl
#                 main_cat_data.append({
#                     'main_cat_id': main_cat_id,
#                     'main_title_name': row[1],
#                     'images': row[2],
#                     'catid': None,
#                     'cat_name': None,
#                     'sub_category': {
#                         'sub_catid': None,
#                         'sub_cat_name': None,
#                     },
#                 })
#     else:
#         error_msg = 'Something Went Wrong'

#     current_url = request.get_full_path()
#     print(f'cat_names::{all_cat_names}')
#     print('-------')
#     print(f'all_sub_cat_names::{all_sub_cat_names}')
#     context = {
#         'main_cat_data': main_cat_data,
#         'all_cat_names': all_cat_names,
#         'all_sub_cat_names': all_sub_cat_names,
#         'current_url': current_url
#     }
#     return render(request, "home_pages/home.html", context)

#All Products
def all_products(request):
    main_cat_query = "SELECT main_cat_id, main_title_name,images FROM vff.united_armor_main_categorytbl ORDER BY main_cat_id"
    main_cat_result = execute_raw_query(main_cat_query)

    all_categories = []
    if not main_cat_result == 500:
        for main_cat_row in main_cat_result:
            main_cat_id = main_cat_row[0]
            main_cat_name = main_cat_row[1]
            main_image = main_cat_row[2]

            cat_query = f"SELECT catid, cat_name FROM vff.united_armor_categorytbl WHERE main_catid = {main_cat_id} ORDER BY catid"
            cat_result = execute_raw_query(cat_query)

            sub_categories = []
            if cat_result and len(cat_result) > 0:
                for cat_row in cat_result:
                    cat_id = cat_row[0]
                    cat_name = cat_row[1]

                    sub_cat_query = f"SELECT sub_catid, sub_cat_name FROM vff.united_armor_sub_categorytbl WHERE catid = {cat_id} ORDER BY sub_catid"
                    sub_cat_result = execute_raw_query(sub_cat_query)

                    sub_cat_data = []
                    if sub_cat_result and len(sub_cat_result) > 0: 
                        for sub_cat_row in sub_cat_result:
                            sub_catid = sub_cat_row[0]
                            sub_cat_name = sub_cat_row[1]
                            
                            sub_cat_data.append({
                                'sub_cat_id': sub_catid,
                                'sub_cat_name': sub_cat_name,
                            })
                            print(f'sub_cat_name::{sub_cat_name}')

                    cat_data = {
                        'cat_id': cat_id,
                        'cat_name': cat_name,
                        'sub_category': sub_cat_data,
                    }
                    sub_categories.append(cat_data)

            main_cat_data = {
                'main_cat_id': main_cat_id,
                'main_cat_name': main_cat_name,
                'images':main_image,
                'categories': sub_categories,
            }
            all_categories.append(main_cat_data)
    else:
        error_msg = 'Something Went Wrong'

    
    # Product Categories Filter
    query_cat = "select product_catid,product_category_name from vff.united_armor_product_categorytbl order by product_catid"
    query_result_cat = execute_raw_query(query_cat)
    product_category_data = []    
    if not query_result_cat == 500:
        for row in query_result_cat:
            
            product_category_data.append({
                'product_catid': row[0],
                'product_category_name': row[1],
                
            })
    else:
        error_msg = 'Something Went Wrong'
    
    # Product Type Filter
    query_type = "select product_type_id,product_type_name from vff.united_armor_product_typetbl order by product_type_id"
    query_result_type = execute_raw_query(query_type)
    product_type_data = []    
    if not query_result_type == 500:
        for row in query_result_type:
            
            product_type_data.append({
                'product_type_id': row[0],
                'product_type_name': row[1],
                
            })
    else:
        error_msg = 'Something Went Wrong'
    
    # Sizes Filter
    query_sizes = "select sizesid,size_value from vff.united_armor_product_sizestbl order by sizesid"
    query_result_sizes = execute_raw_query(query_sizes)
    sizes_filter_data = []    
    if not query_result_sizes == 500:
        for row in query_result_sizes:
            
            sizes_filter_data.append({
                'sizes_id': row[0],
                'size_value': row[1],
                
            })
    else:
        error_msg = 'Something Went Wrong'
    
    # Color Filter
    query_color = "select colorsid,color_name,color_code from vff.united_armor_product_colorstbl"
    query_result_color = execute_raw_query(query_color)
    color_filter_data = []    
    if not query_result_color == 500:
        for row in query_result_color:
            
            color_filter_data.append({
                'colors_id': row[0],
                'color_name': row[1],
                'color_code': row[2],
                
            })
    else:
        error_msg = 'Something Went Wrong'
     
    current_url = request.get_full_path()
    context = {'all_categories': all_categories,'product_category_data':product_category_data,'product_type_data':product_type_data,'sizes_filter_data':sizes_filter_data,'color_filter_data':color_filter_data, 'current_url': current_url}
    return render(request,"product_pages/all_products.html",context)

#All Products With Main Category Wise
def all_products_with_main_category(request,s_main_cat_id,s_main_cat_name):
    main_cat_query = "SELECT main_cat_id, main_title_name,images FROM vff.united_armor_main_categorytbl ORDER BY main_cat_id"
    main_cat_result = execute_raw_query(main_cat_query)

    all_categories = []
    if not main_cat_result == 500:
        for main_cat_row in main_cat_result:
            main_cat_id = main_cat_row[0]
            main_cat_name = main_cat_row[1]
            main_image = main_cat_row[2]

            cat_query = f"SELECT catid, cat_name FROM vff.united_armor_categorytbl WHERE main_catid = {main_cat_id} ORDER BY catid"
            cat_result = execute_raw_query(cat_query)

            sub_categories = []
            if cat_result and len(cat_result) > 0:
                for cat_row in cat_result:
                    cat_id = cat_row[0]
                    cat_name = cat_row[1]

                    sub_cat_query = f"SELECT sub_catid, sub_cat_name FROM vff.united_armor_sub_categorytbl WHERE catid = {cat_id} ORDER BY sub_catid"
                    sub_cat_result = execute_raw_query(sub_cat_query)

                    sub_cat_data = []
                    if sub_cat_result and len(sub_cat_result) > 0: 
                        for sub_cat_row in sub_cat_result:
                            sub_catid = sub_cat_row[0]
                            sub_cat_name = sub_cat_row[1]
                            
                            sub_cat_data.append({
                                'sub_cat_id': sub_catid,
                                'sub_cat_name': sub_cat_name,
                            })
                            # print(f'sub_cat_name::{sub_cat_name}')

                    cat_data = {
                        'cat_id': cat_id,
                        'cat_name': cat_name,
                        'sub_category': sub_cat_data,
                    }
                    sub_categories.append(cat_data)

            main_cat_data = {
                'main_cat_id': main_cat_id,
                'main_cat_name': main_cat_name,
                'images':main_image,
                'categories': sub_categories,
            }
            all_categories.append(main_cat_data)
    else:
        error_msg = 'Something Went Wrong'

    
    # Product Categories Filter
    query_cat = "select product_catid,product_category_name from vff.united_armor_product_categorytbl order by product_catid"
    query_result_cat = execute_raw_query(query_cat)
    product_category_data = []    
    if not query_result_cat == 500:
        for row in query_result_cat:
            
            product_category_data.append({
                'product_catid': row[0],
                'product_category_name': row[1],
                
            })
    else:
        error_msg = 'Something Went Wrong'
    
    # Product Type Filter
    query_type = "select product_type_id,product_type_name from vff.united_armor_product_typetbl order by product_type_id"
    query_result_type = execute_raw_query(query_type)
    product_type_data = []    
    if not query_result_type == 500:
        for row in query_result_type:
            
            product_type_data.append({
                'product_type_id': row[0],
                'product_type_name': row[1],
                
            })
    else:
        error_msg = 'Something Went Wrong'
    
    # Sizes Filter
    query_sizes = "select sizesid,size_value from vff.united_armor_product_sizestbl order by sizesid"
    query_result_sizes = execute_raw_query(query_sizes)
    sizes_filter_data = []    
    if not query_result_sizes == 500:
        for row in query_result_sizes:
            
            sizes_filter_data.append({
                'sizes_id': row[0],
                'size_value': row[1],
                
            })
    else:
        error_msg = 'Something Went Wrong'
    
    # Color Filter
    query_color = "select colorsid,color_name,color_code from vff.united_armor_product_colorstbl"
    query_result_color = execute_raw_query(query_color)
    color_filter_data = []    
    if not query_result_color == 500:
        for row in query_result_color:
            
            color_filter_data.append({
                'colors_id': row[0],
                'color_name': row[1],
                'color_code': row[2],
                
            })
    else:
        error_msg = 'Something Went Wrong'
        
    
    # All Products For Main Category
    query_product = "SELECT productid,product_name,fitting_type,fitting_id,main_title_name,cat_name,sub_cat_name,product_catid,product_category_name,united_armor_all_productstbl.product_type_id,product_type_name,price,united_armor_all_productstbl.main_cat_id,united_armor_all_productstbl.cat_id,united_armor_all_productstbl.sub_catid,offer_price,default_images,default_size,ratings,default_color_id,color_name,color_code FROM vff.united_armor_product_colorstbl,vff.united_armor_all_productstbl,vff.united_armor_product_categorytbl,vff.united_armor_product_typetbl,vff.united_armor_main_categorytbl,vff.united_armor_categorytbl,vff.united_armor_sub_categorytbl WHERE united_armor_product_colorstbl.colorsid=default_color_id  AND united_armor_product_categorytbl.product_catid=united_armor_all_productstbl.product_collection_id AND united_armor_product_typetbl.product_type_id=united_armor_all_productstbl.product_type_id AND united_armor_main_categorytbl.main_cat_id=united_armor_all_productstbl.main_cat_id AND united_armor_all_productstbl.cat_id=united_armor_categorytbl.catid AND united_armor_all_productstbl.sub_catid=united_armor_sub_categorytbl.sub_catid AND united_armor_all_productstbl.main_cat_id='"+str(s_main_cat_id)+"' and added_to_inventory='1' order by productid desc"
    query_result_product = execute_raw_query(query_product)
    all_product_data = []    
    if not query_result_product == 500:
        for row in query_result_product:
            
            all_product_data.append({
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
                    'offer_price':row[15],
                    'image':row[16],
                    'size':row[17],
                    'ratings':row[18],
                    'default_color_id':row[19],
                    'color_name':row[20],
                    'color_code':row[21],
                
            })
    else:
        error_msg = 'Something Went Wrong'
     
    current_url = request.get_full_path()
    context = {'all_categories': all_categories,'product_category_data':product_category_data,'product_type_data':product_type_data,'sizes_filter_data':sizes_filter_data,'color_filter_data':color_filter_data, 'current_url': current_url,'s_main_cat_id':s_main_cat_id,'s_main_cat_name':s_main_cat_name,'all_product_data':all_product_data}
    return render(request,"product_pages/all_products.html",context)

#All Products with Category Wise
def all_products_with_category(request,s_main_cat_id,s_main_cat_name,s_cat_id,s_cat_name):
    main_cat_query = "SELECT main_cat_id, main_title_name,images FROM vff.united_armor_main_categorytbl ORDER BY main_cat_id"
    main_cat_result = execute_raw_query(main_cat_query)

    all_categories = []
    if not main_cat_result == 500:
        for main_cat_row in main_cat_result:
            main_cat_id = main_cat_row[0]
            main_cat_name = main_cat_row[1]
            main_image = main_cat_row[2]

            cat_query = f"SELECT catid, cat_name FROM vff.united_armor_categorytbl WHERE main_catid = {main_cat_id} ORDER BY catid"
            cat_result = execute_raw_query(cat_query)

            sub_categories = []
            if cat_result and len(cat_result) > 0:
                for cat_row in cat_result:
                    cat_id = cat_row[0]
                    cat_name = cat_row[1]

                    sub_cat_query = f"SELECT sub_catid, sub_cat_name FROM vff.united_armor_sub_categorytbl WHERE catid = {cat_id} ORDER BY sub_catid"
                    sub_cat_result = execute_raw_query(sub_cat_query)

                    sub_cat_data = []
                    if sub_cat_result and len(sub_cat_result) > 0: 
                        for sub_cat_row in sub_cat_result:
                            sub_catid = sub_cat_row[0]
                            sub_cat_name = sub_cat_row[1]
                            
                            sub_cat_data.append({
                                'sub_cat_id': sub_catid,
                                'sub_cat_name': sub_cat_name,
                            })
                            print(f'sub_cat_name::{sub_cat_name}')

                    cat_data = {
                        'cat_id': cat_id,
                        'cat_name': cat_name,
                        'sub_category': sub_cat_data,
                    }
                    sub_categories.append(cat_data)

            main_cat_data = {
                'main_cat_id': main_cat_id,
                'main_cat_name': main_cat_name,
                'images':main_image,
                'categories': sub_categories,
            }
            all_categories.append(main_cat_data)
    else:
        error_msg = 'Something Went Wrong'

    
    # Product Categories Filter
    query_cat = "select product_catid,product_category_name from vff.united_armor_product_categorytbl order by product_catid"
    query_result_cat = execute_raw_query(query_cat)
    product_category_data = []    
    if not query_result_cat == 500:
        for row in query_result_cat:
            
            product_category_data.append({
                'product_catid': row[0],
                'product_category_name': row[1],
                
            })
    else:
        error_msg = 'Something Went Wrong'
    
    # Product Type Filter
    query_type = "select product_type_id,product_type_name from vff.united_armor_product_typetbl order by product_type_id"
    query_result_type = execute_raw_query(query_type)
    product_type_data = []    
    if not query_result_type == 500:
        for row in query_result_type:
            
            product_type_data.append({
                'product_type_id': row[0],
                'product_type_name': row[1],
                
            })
    else:
        error_msg = 'Something Went Wrong'
    
    # Sizes Filter
    query_sizes = "select sizesid,size_value from vff.united_armor_product_sizestbl order by sizesid"
    query_result_sizes = execute_raw_query(query_sizes)
    sizes_filter_data = []    
    if not query_result_sizes == 500:
        for row in query_result_sizes:
            
            sizes_filter_data.append({
                'sizes_id': row[0],
                'size_value': row[1],
                
            })
    else:
        error_msg = 'Something Went Wrong'
    
    # Color Filter
    query_color = "select colorsid,color_name,color_code from vff.united_armor_product_colorstbl"
    query_result_color = execute_raw_query(query_color)
    color_filter_data = []    
    if not query_result_color == 500:
        for row in query_result_color:
            
            color_filter_data.append({
                'colors_id': row[0],
                'color_name': row[1],
                'color_code': row[2],
                
            })
    else:
        error_msg = 'Something Went Wrong'
     
    current_url = request.get_full_path()
    context = {'all_categories': all_categories,'product_category_data':product_category_data,'product_type_data':product_type_data,'sizes_filter_data':sizes_filter_data,'color_filter_data':color_filter_data, 'current_url': current_url}
    return render(request,"product_pages/all_products.html",context)

#All Products with Sub Category Wise
def all_products_with_sub_category(request,s_main_cat_id,s_main_cat_name,s_cat_id,s_cat_name,s_sub_cat_id,s_sub_cat_name):
    main_cat_query = "SELECT main_cat_id, main_title_name,images FROM vff.united_armor_main_categorytbl ORDER BY main_cat_id"
    main_cat_result = execute_raw_query(main_cat_query)

    all_categories = []
    if not main_cat_result == 500:
        for main_cat_row in main_cat_result:
            main_cat_id = main_cat_row[0]
            main_cat_name = main_cat_row[1]
            main_image = main_cat_row[2]

            cat_query = f"SELECT catid, cat_name FROM vff.united_armor_categorytbl WHERE main_catid = {main_cat_id} ORDER BY catid"
            cat_result = execute_raw_query(cat_query)

            sub_categories = []
            if cat_result and len(cat_result) > 0:
                for cat_row in cat_result:
                    cat_id = cat_row[0]
                    cat_name = cat_row[1]

                    sub_cat_query = f"SELECT sub_catid, sub_cat_name FROM vff.united_armor_sub_categorytbl WHERE catid = {cat_id} ORDER BY sub_catid"
                    sub_cat_result = execute_raw_query(sub_cat_query)

                    sub_cat_data = []
                    if sub_cat_result and len(sub_cat_result) > 0: 
                        for sub_cat_row in sub_cat_result:
                            sub_catid = sub_cat_row[0]
                            sub_cat_name = sub_cat_row[1]
                            
                            sub_cat_data.append({
                                'sub_cat_id': sub_catid,
                                'sub_cat_name': sub_cat_name,
                            })
                            # print(f'sub_cat_name::{sub_cat_name}')

                    cat_data = {
                        'cat_id': cat_id,
                        'cat_name': cat_name,
                        'sub_category': sub_cat_data,
                    }
                    sub_categories.append(cat_data)

            main_cat_data = {
                'main_cat_id': main_cat_id,
                'main_cat_name': main_cat_name,
                'images':main_image,
                'categories': sub_categories,
            }
            all_categories.append(main_cat_data)
    else:
        error_msg = 'Something Went Wrong'

    
    # Product Categories Filter
    query_cat = "select product_catid,product_category_name from vff.united_armor_product_categorytbl order by product_catid"
    query_result_cat = execute_raw_query(query_cat)
    product_category_data = []    
    if not query_result_cat == 500:
        for row in query_result_cat:
            
            product_category_data.append({
                'product_catid': row[0],
                'product_category_name': row[1],
                
            })
    else:
        error_msg = 'Something Went Wrong'
    
    # Product Type Filter
    query_type = "select product_type_id,product_type_name from vff.united_armor_product_typetbl order by product_type_id"
    query_result_type = execute_raw_query(query_type)
    product_type_data = []    
    if not query_result_type == 500:
        for row in query_result_type:
            
            product_type_data.append({
                'product_type_id': row[0],
                'product_type_name': row[1],
                
            })
    else:
        error_msg = 'Something Went Wrong'
    
    # Sizes Filter
    query_sizes = "select sizesid,size_value from vff.united_armor_product_sizestbl order by sizesid"
    query_result_sizes = execute_raw_query(query_sizes)
    sizes_filter_data = []    
    if not query_result_sizes == 500:
        for row in query_result_sizes:
            
            sizes_filter_data.append({
                'sizes_id': row[0],
                'size_value': row[1],
                
            })
    else:
        error_msg = 'Something Went Wrong'
    
    # Color Filter
    query_color = "select colorsid,color_name,color_code from vff.united_armor_product_colorstbl"
    query_result_color = execute_raw_query(query_color)
    color_filter_data = []    
    if not query_result_color == 500:
        for row in query_result_color:
            
            color_filter_data.append({
                'colors_id': row[0],
                'color_name': row[1],
                'color_code': row[2],
                
            })
    else:
        error_msg = 'Something Went Wrong'
        
    # All Products For Sub Category
    query_product = "SELECT productid,product_name,fitting_type,fitting_id,main_title_name,cat_name,sub_cat_name,product_catid,product_category_name,united_armor_all_productstbl.product_type_id,product_type_name,price,united_armor_all_productstbl.main_cat_id,united_armor_all_productstbl.cat_id,united_armor_all_productstbl.sub_catid,offer_price,default_images,default_size,ratings,default_color_id,color_name,color_code FROM vff.united_armor_product_colorstbl,vff.united_armor_all_productstbl,vff.united_armor_product_categorytbl,vff.united_armor_product_typetbl,vff.united_armor_main_categorytbl,vff.united_armor_categorytbl,vff.united_armor_sub_categorytbl WHERE united_armor_product_colorstbl.colorsid=default_color_id  AND united_armor_product_categorytbl.product_catid=united_armor_all_productstbl.product_collection_id AND united_armor_product_typetbl.product_type_id=united_armor_all_productstbl.product_type_id AND united_armor_main_categorytbl.main_cat_id=united_armor_all_productstbl.main_cat_id AND united_armor_all_productstbl.cat_id=united_armor_categorytbl.catid AND united_armor_all_productstbl.sub_catid=united_armor_sub_categorytbl.sub_catid AND united_armor_all_productstbl.sub_catid='"+str(s_sub_cat_id)+"' and added_to_inventory='1' order by productid desc"
    query_result_product = execute_raw_query(query_product)
    all_product_data = []    
    if not query_result_product == 500:
        for row in query_result_product:
            
            all_product_data.append({
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
                    'offer_price':row[15],
                    'image':row[16],
                    'size':row[17],
                    'ratings':row[18],
                    'default_color_id':row[19],
                    'color_name':row[20],
                    'color_code':row[21],
                
            })
    else:
        error_msg = 'Something Went Wrong'
     
    current_url = request.get_full_path()
    context = {'all_categories': all_categories,'product_category_data':product_category_data,'product_type_data':product_type_data,'sizes_filter_data':sizes_filter_data,'color_filter_data':color_filter_data, 'current_url': current_url,'s_main_cat_id':s_main_cat_id,'s_main_cat_name':s_main_cat_name,'s_cat_id':s_cat_id,'s_cat_name':s_cat_name,'s_sub_cat_id':s_sub_cat_id,'s_sub_cat_name':s_sub_cat_name,'all_product_data':all_product_data}
    return render(request,"product_pages/all_products.html",context)

#Single Product Detail with Product ID
def product(request,product_id):
    error_msg = 'No Product Details Found'
    main_cat_query = "SELECT main_cat_id, main_title_name,images FROM vff.united_armor_main_categorytbl ORDER BY main_cat_id"
    main_cat_result = execute_raw_query(main_cat_query)

    all_categories = []
    if not main_cat_result == 500:
        for main_cat_row in main_cat_result:
            main_cat_id = main_cat_row[0]
            main_cat_name = main_cat_row[1]
            main_image = main_cat_row[2]

            cat_query = f"SELECT catid, cat_name FROM vff.united_armor_categorytbl WHERE main_catid = {main_cat_id} ORDER BY catid"
            cat_result = execute_raw_query(cat_query)

            sub_categories = []
            if cat_result and len(cat_result) > 0:
                for cat_row in cat_result:
                    cat_id = cat_row[0]
                    cat_name = cat_row[1]

                    sub_cat_query = f"SELECT sub_catid, sub_cat_name FROM vff.united_armor_sub_categorytbl WHERE catid = {cat_id} ORDER BY sub_catid"
                    sub_cat_result = execute_raw_query(sub_cat_query)

                    sub_cat_data = []
                    if sub_cat_result and len(sub_cat_result) > 0: 
                        for sub_cat_row in sub_cat_result:
                            sub_catid = sub_cat_row[0]
                            sub_cat_name = sub_cat_row[1]
                            
                            sub_cat_data.append({
                                'sub_cat_id': sub_catid,
                                'sub_cat_name': sub_cat_name,
                            })
                            print(f'sub_cat_name::{sub_cat_name}')

                    cat_data = {
                        'cat_id': cat_id,
                        'cat_name': cat_name,
                        'sub_category': sub_cat_data,
                    }
                    sub_categories.append(cat_data)

            main_cat_data = {
                'main_cat_id': main_cat_id,
                'main_cat_name': main_cat_name,
                'images':main_image,
                'categories': sub_categories,
            }
            all_categories.append(main_cat_data)
    else:
        error_msg = 'Something Went Wrong'

    
    query = "SELECT product_name,fitting_type,fitting_id,max_checkout_qty,what_it_does,specifications,fit_and_care_desc,main_title_name,cat_name,sub_cat_name,product_catid,product_category_name,united_armor_all_productstbl.product_type_id,product_type_name,price,united_armor_all_productstbl.main_cat_id,united_armor_all_productstbl.cat_id,united_armor_all_productstbl.sub_catid,offer_price,default_images,default_size,ratings,default_color_id,color_name,color_code,measurementid,image_url FROM  vff.united_armor_measurementtbl,vff.united_armor_product_colorstbl,vff.united_armor_all_productstbl,vff.united_armor_product_categorytbl,vff.united_armor_product_typetbl,vff.united_armor_main_categorytbl,vff.united_armor_categorytbl,vff.united_armor_sub_categorytbl WHERE united_armor_measurementtbl.measurementid=united_armor_all_productstbl.measurement_id and united_armor_product_colorstbl.colorsid=default_color_id  AND united_armor_product_categorytbl.product_catid=united_armor_all_productstbl.product_collection_id AND united_armor_product_typetbl.product_type_id=united_armor_all_productstbl.product_type_id AND united_armor_main_categorytbl.main_cat_id=united_armor_all_productstbl.main_cat_id AND united_armor_all_productstbl.cat_id=united_armor_categorytbl.catid AND united_armor_all_productstbl.sub_catid=united_armor_sub_categorytbl.sub_catid AND productid='"+str(product_id)+"'"
    query_result = execute_raw_query(query)
    data = []    
    if not query_result == 500:
        for row in query_result:
            specifications_list = row[5].split('.') if '.' in row[5] else [row[5]]
            fit_and_care_list = row[6].split('.') if '.' in row[6] else [row[6]]
            data.append({
                    'product_name':row[0],
                    'fitting_type':row[1],
                    'fitting_id':row[2],
                    'max_checkout_qty':row[3],
                    'what_it_does':row[4],
                    'specifications':specifications_list,
                    'fit_and_care_desc':fit_and_care_list,
                    'main_title_name':row[7],
                    'cat_name':row[8],
                    'sub_cat_name':row[9],
                    'product_catid':row[10],
                    'product_category_name':row[11],
                    'product_type_id':row[12],
                    'product_type_name':row[13],
                    'price':row[14],
                    'main_cat_id':row[15],
                    'cat_id':row[16],
                    'sub_catid':row[17],
                    'offer_price':row[18],
                    'image':row[19],
                    'size':row[20],
                    'ratings':row[21],
                    'default_color_id':row[22],
                    'color_name':row[23],
                    'color_code':row[24],
                    'measurement_id':row[25],
                    'size_guide_image_url':row[26],
                
            })
    else:
        error_msg = 'Something Went Wrong'
    color_id = data[0]['default_color_id'] if data else ''
    #All Sizes for a particular product id and color id
    query_size="select sizesid,size_value,reserved_quantity,stock_status,united_armor_inventorytbl.color_id from vff.united_armor_inventorytbl,vff.united_armor_product_sizestbl,vff.united_armor_sizes_available where united_armor_product_sizestbl.sizesid=united_armor_sizes_available.sizeid and united_armor_inventorytbl.product_id=united_armor_sizes_available.product_id and united_armor_sizes_available.color_id=united_armor_inventorytbl.color_id and united_armor_sizes_available.sizeid=united_armor_inventorytbl.size_id and united_armor_inventorytbl.product_id='"+str(product_id)+"'  order by sizesid"
    query_result_size = execute_raw_query(query_size)
    data_sizes = []    
    if not query_result_size == 500:
        for row in query_result_size:
            
            data_sizes.append({
                    'sizesid':row[0],
                    'size_value':row[1],
                    'quantity_available':row[2],
                    'stock_status':row[3],
                    'size_color_id':row[4],
                   
                
            })
    else:
        error_msg = 'Something Went Wrong'
    
    #all Images
    query_images="select imageid,image_url,color_id from vff.united_armor_product_imagestbl where product_id='"+str(product_id)+"' order by imageid"
    query_result_images = execute_raw_query(query_images)
    data_images = []    
    if not query_result_images == 500:
        for row in query_result_images:
            
            data_images.append({
                    'image_id':row[0],
                    'image_url':row[1],
                    'color_id_image':row[2],
                   
                
            })
    else:
        error_msg = 'Something Went Wrong'
    
    #colors available for a particular color
    query_color = "select colorsid,color_name,color_code from vff.united_armor_product_colorstbl where product_id='"+str(product_id)+"'"
    query_result_color = execute_raw_query(query_color)
    data_colors = []    
    if not query_result_color == 500:
        for row in query_result_color:
            
            data_colors.append({
                    'colorsid':row[0],
                    'color_name':row[1],
                    'color_code':row[2],
                   
                
            })
    else:
        error_msg = 'Something Went Wrong'
    
    # Review for this product
    query_review = "select review_id,customer_id,customer_name,comment,ratings,time_review_given from vff.united_armor_product_reviewtbl,vff.united_armor_customertbl where united_armor_customertbl.customerid=united_armor_product_reviewtbl.customer_id and product_id='"+str(product_id)+"'"
    query_result_review = execute_raw_query(query_review)
    review_data = []    
    if not query_result_review == 500:
        for row in query_result_review:
            timestamp = row[5]
            days_back = calculate_time_difference(timestamp)
            review_data.append({
                    'review_id':row[0],
                    'customer_id':row[1],
                    'customer_name':row[2],
                    'comment':row[3],
                    'ratings':row[4],
                    'time_review_given':days_back,
                   
                
            })
    else:
        error_msg = 'Something Went Wrong'
        
    #customer ID
    customer_id = request.session.get('u_customer_id')
    print(f'customer_id:::{customer_id}')
    if customer_id == None:
        customer_id = ''
    
    current_url = request.get_full_path()
    context = {'all_categories': all_categories,'query_result':data,'review_data':review_data,'data_images':data_images,'data_sizes':data_sizes,'data_colors':data_colors, 'current_url': current_url,'error_msg':error_msg,'customer_id':customer_id}
    return render(request,"product_pages/single_product.html",context)

#Wish List Details Against Customer ID
def wishlist_details(request):
    #select wishlistid,united_armor_wishlisttbl.product_id,product_name,price,offer_price,default_images,default_size,colorsid,color_name,color_code from vff.united_armor_product_colorstbl,vff.united_armor_wishlisttbl,vff.united_armor_all_productstbl where united_armor_wishlisttbl.product_id=united_armor_all_productstbl.productid and united_armor_product_colorstbl.product_id=united_armor_all_productstbl.productid and united_armor_wishlisttbl.product_id=united_armor_product_colorstbl.product_id and united_armor_wishlisttbl.color_id=united_armor_product_colorstbl.colorsid and customer_id='1000000'
    
    error_msg = 'No Item Added To Wishlist'
    #Getting Customer ID from Session
    customer_id = request.session.get('u_customer_id')
    if customer_id == '' or customer_id == None:
        customer_id = 1000000
    query = "select wishlistid,united_armor_wishlisttbl.product_id,product_name,price,offer_price,default_images,default_size,colorsid,color_name,color_code from vff.united_armor_product_colorstbl,vff.united_armor_wishlisttbl,vff.united_armor_all_productstbl where united_armor_wishlisttbl.product_id=united_armor_all_productstbl.productid and united_armor_product_colorstbl.product_id=united_armor_all_productstbl.productid and united_armor_wishlisttbl.product_id=united_armor_product_colorstbl.product_id and united_armor_wishlisttbl.color_id=united_armor_product_colorstbl.colorsid and customer_id='"+str(customer_id)+"' order by wishlistid desc"
    query_result = execute_raw_query(query)
    data = []    
    if not query_result == 500:
        for row in query_result:
            
            data.append({
                    'wishlist_id':row[0],
                    'product_id':row[1],
                    'product_name':row[2],
                    'price':row[3],
                    'offer_price':row[4],
                    'default_images':row[5],
                    'default_size':row[6],
                    'colorsid':row[7],
                    'color_name':row[8],
                    'color_code':row[9],
                
            })
    else:
        error_msg = 'Something Went Wrong'
    current_url = request.get_full_path()
    context= {'current_url': current_url,'query_result':data,'error_msg':error_msg}
    return render(request,"wishlist_pages/wishlist.html",context)

#Delete From Wish List 
def delete_from_wishlist(request,wishlist_id):
    try:
        with connection.cursor() as cursor:
            
            # Add Item To Wish list
            insert_query = "delete from vff.united_armor_wishlisttbl where wishlistid='"+str(wishlist_id)+"'"
            
            print(f"deleting from wish list::{insert_query}")
            cursor.execute(insert_query)
            connection.commit()
            print("Item Delete from Wish List Successfully.")
            return JsonResponse({'message':'Item Delete from  Wish List successfully'})
    except Exception as e:
        print(f"Error loading data: {e}")
    return JsonResponse({'message':'Oops Something Went Wrong'})

#Cart Details against Usrid
def cart_details(request):
    current_url = request.get_full_path()
    return render(request,"cart_pages/cart.html",{'current_url': current_url})

#Checkout Page
def checkout(request):
    current_url = request.get_full_path()
    return render(request,"checkout_pages/checkout.html",{'current_url': current_url})

#4 0 4 Page
def custom_404_view_united(request, exception=None):
    return render(request, 'error_pages/404.html', status=404)

#5 0 0 Page
def custom_500_view_united(request, exception=None):
    return render(request, 'error_pages/500.html', status=500)

# Add To wishlist 
def add_to_wishlist(request,product_id,color_id):
    
    #If he is a guest user then the customer id will be 1000000
    customer_id = request.session.get('u_customer_id')
    if customer_id == '' or customer_id == None:
        customer_id = 1000000
    try:
        with connection.cursor() as cursor:
            
            # Add Item To Wish list
            insert_query = "insert into vff.united_armor_wishlisttbl(product_id,customer_id,color_id) values ('"+str(product_id)+"','"+str(customer_id)+"','"+str(color_id)+"')"
            
            print(f"adding to wish list::{insert_query}")
            cursor.execute(insert_query)
            connection.commit()
            print("Item Added To Wish List Successfully.")
            return JsonResponse({'message':'Item Added To  Wish List successfully'})
    except Exception as e:
        print(f"Error loading data: {e}")
    return JsonResponse({'message':'Oops Something Went Wrong'})

# Add To Cart 
def add_to_cart(request,product_id,color_id,size_id,price,quantity,offer_price):
    # Convert path parameters to float
    price = float(price)
    offer_price = float(offer_price)
    actual_price = price
    #If he is a guest user then the customer id will be 1000000
    customer_id = request.session.get('u_customer_id')
    if customer_id == '' or customer_id == None:
        customer_id = 1000000
    try:
        with connection.cursor() as cursor:
            if offer_price != 0.0:
                price = offer_price
            # Adding Item to Cart
            insert_query = "insert into vff.united_armor_cart_tbl(product_id,customer_id,price,color_id,size_id,quantity,offer_price,actual_price) values ('"+str(product_id)+"','"+str(customer_id)+"','"+str(price)+"','"+str(color_id)+"','"+str(size_id)+"','"+str(quantity)+"','"+str(offer_price)+"','"+str(actual_price)+"')"
            
            print(f"adding to cart Id::{insert_query}")
            cursor.execute(insert_query)
            connection.commit()
            print("Item Added To Cart Successfully.")
            return JsonResponse({'message':'Item Added to cart successfully'})
    except Exception as e:
        print(f"Error loading data: {e}")
    return JsonResponse({'message':'Oops Something Went Wrong'})

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

from datetime import datetime

def format_time_difference(time_difference):
    if time_difference < 1:
        return 'just now'
    elif time_difference == 1:
        return '1 day ago'
    elif time_difference < 60:
        return f'{time_difference} minutes ago'
    elif time_difference < 1440:
        return f'{time_difference // 60} hours ago'
    else:
        return f'{time_difference // 1440} days ago'

def calculate_time_difference(timestamp):
    # Assuming timestamp is in seconds
    review_date = datetime.utcfromtimestamp(timestamp)

    # Get current date and time
    current_date = datetime.utcnow()

    # Calculate the difference in minutes
    minutes_difference = int((current_date - review_date).total_seconds() / 60)

    # Format the time difference
    formatted_time_difference = format_time_difference(minutes_difference)

    return formatted_time_difference


