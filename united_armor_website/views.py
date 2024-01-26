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
        query = "select customerid,customer_name from vff.united_armor_customertbl where email='"+str(username)+"' "
        user_data = execute_raw_query_fetch_one(query)
        if user_data :
                # User is authorized
                print('User is Authorized')
                request.session['u_customer_id'] = user_data[0]
                request.session['customer_name'] = user_data[1]
                return JsonResponse({'message': 'Login successful'})        
        else:
            error_msg = 'Something Went Wrong'
            return JsonResponse({'message': 'Invalid credentials'})
        
        
    else:
        # Handle other HTTP methods if needed
        return JsonResponse({'message': 'Something Went Wrong'})
    
def handle_register(request):
    if request.method == 'POST':
        name = request.POST.get('register-name')
        email = request.POST.get('register-email')
        password = request.POST.get('register-password')

        # Perform your login logic here
        query = "select customerid,customer_name from vff.united_armor_customertbl where email='"+str(email)+"' "
        user_data = execute_raw_query_fetch_one(query)
        if user_data :
                return JsonResponse({'message': 'Already Exist'})        
        else:
            try:
                with connection.cursor() as cursor:
                    
                    # Add Item To Wish list
                    insert_query = "insert into vff.united_armor_customertbl(customer_name,email,password) values ('"+str(name)+"','"+str(email)+"','"+str(password)+"') returning customerid"
                    
                    print(f"New User Register::{insert_query}")
                    cursor.execute(insert_query)
                    customer_id = cursor.fetchone()[0] 
                    connection.commit()
                    request.session['u_customer_id'] = customer_id
                    request.session['customer_name'] = name
                    print("Customer Registered  Successfully.")
                    return JsonResponse({'message':'Registered Successfully'})
            except Exception as e:
                print(f"Error loading data: {e}")
                return JsonResponse({'message': 'Something Went Wrong'})
                
            
        
        
    else:
        # Handle other HTTP methods if needed
        return JsonResponse({'message': 'Something Went Wrong'})
    
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
    context = {'all_categories': all_categories,'product_id':product_id,'query_result':data,'review_data':review_data,'data_images':data_images,'data_sizes':data_sizes,'data_colors':data_colors, 'current_url': current_url,'error_msg':error_msg,'customer_id':customer_id}
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

# Add to cart
def add_to_cart(request):
    if request.method == 'POST':
        try:
            # Get the JSON data sent in the request
            json_data = json.loads(request.POST.get('selectedProduct'))

            # Access individual values from the JSON data
            product_id = json_data['productID']
            product_name = json_data['productName']
            selected_color_image = json_data['selectedColorImage']
            price = json_data['price']
            offer_price = json_data['offerPrice']
            selected_color_id = json_data['selectedColorId']
            selected_size_id = json_data['selectedSizeId']
            quantity = int(json_data['quantity'])
            
            # Remove the ₹ symbol and any other non-numeric characters
            price = float(price.replace('₹', '').replace(',', ''))
            offer_price = float(offer_price.replace('₹', '').replace(',', ''))
            total_price = quantity * price
            
            if offer_price != 0.0 or offer_price !=0:
                total_price = quantity * offer_price
            customer_id = request.session.get('u_customer_id')
            try:
                with connection.cursor() as cursor:
                    
                    # Add Item To Wish list
                    insert_query = "insert into vff.united_armor_cart_tbl(product_id,quantity,customer_id,price,color_id,size_id,offer_price,actual_price,product_img_url) values ('"+str(product_id)+"','"+str(quantity)+"','"+str(customer_id)+"','"+str(total_price)+"','"+str(selected_color_id)+"','"+str(selected_size_id)+"','"+str(offer_price)+"','"+str(price)+"','"+str(selected_color_image)+"')"
                    
                    print(f"Add To Cart ::{insert_query}")
                    cursor.execute(insert_query)
                    connection.commit()
                    print("Add To Cart Successfully.")
                    return JsonResponse({'message':'Added To Cart successfully'})
            except Exception as e:
                print(f"Error loading data: {e}")
                return JsonResponse({'message':'Oops Something Went Wrong'})
        except Exception as e:
            # Handle exceptions (e.g., invalid JSON, missing keys, etc.)
            print(f"Add to cart error{e}")
            return JsonResponse({'error': str(e)}, status=400)
    return JsonResponse({'message':'Oops Something Went Wrong'})

#Update Cart Items 
def update_cart(request):
    if request.method == "POST":
        try:
            with connection.cursor() as cursor:
                cart_id = request.POST.get('cart_id')
                quantity = request.POST.get('quantity')
                # Convert quantity to an integer
                quantity = int(quantity)
                price = request.POST.get('price')
                price = float(price.replace('₹', '').replace(',', ''))
                total_price = quantity * price
                # Update Cart item Price and Quantity where cartid 
                update_query = "update  vff.united_armor_cart_tbl set quantity='"+str(quantity)+"', price='"+str(total_price)+"' where cartid='"+str(cart_id)+"'"
                
                print(f"Update Cart Item Details::{update_query}")
                cursor.execute(update_query)
                connection.commit()
                print("Cart Item Updated Successfully.")
                return JsonResponse({'message':'success'})
        except Exception as e:
            print(f"Error loading data: {e}")
    return JsonResponse({'message':'error'})


#Remove From Cart Items 
def remove_cart_item(request):
    if request.method == "POST":
        try:
            with connection.cursor() as cursor:
                cart_id = request.POST.get('cart_id')
                # Remove item from cart where cartid
                delete_query = "delete from vff.united_armor_cart_tbl where cartid='"+str(cart_id)+"';"
                
                print(f"deleting from cart::{delete_query}")
                cursor.execute(delete_query)
                connection.commit()
                print("Item Delete from cart Successfully.")
                return JsonResponse({'message':'success'})
        except Exception as e:
            print(f"Error loading data: {e}")
        return JsonResponse({'message':'error'})


#Cart Details against Usrid
def cart_details(request):
    error_msg = 'No Items Found in Cart'
    customer_id = request.session.get("u_customer_id")
    if customer_id == None:
        error_msg = 'Please Login To Add Items to Cart'
        context = {'query_result':[],'error_msg':error_msg}
        return render(request,"cart_pages/cart.html",context)
    query = "select cartid,united_armor_cart_tbl.product_id,product_name,quantity,max_checkout_qty,united_armor_cart_tbl.price,color_name,product_img_url,reserved_quantity,stock_status,size_value,actual_price,united_armor_cart_tbl.offer_price from vff.united_armor_inventorytbl,vff.united_armor_cart_tbl,vff.united_armor_all_productstbl,vff.united_armor_product_sizestbl,vff.united_armor_product_colorstbl where united_armor_product_sizestbl.sizesid=united_armor_cart_tbl.size_id and united_armor_product_colorstbl.colorsid=united_armor_cart_tbl.color_id and united_armor_product_colorstbl.product_id=united_armor_all_productstbl.productid and united_armor_product_colorstbl.product_id=united_armor_cart_tbl.product_id and united_armor_cart_tbl.product_id=united_armor_all_productstbl.productid and united_armor_inventorytbl.product_id=united_armor_all_productstbl.productid and united_armor_inventorytbl.product_id=united_armor_cart_tbl.product_id and united_armor_inventorytbl.color_id=united_armor_cart_tbl.color_id and united_armor_inventorytbl.size_id=united_armor_cart_tbl.size_id and  customer_id='"+str(customer_id)+"'  order by cartid desc"
    query_result = execute_raw_query(query)
    data = []    
    if not query_result == 500:
        for row in query_result:
            actual_price = row[11]
            offer_price = row[12]
            per_item_price= actual_price
            if offer_price !=0.0 or offer_price !=0:
                per_item_price = offer_price
            data.append({
                    'cart_id':row[0],
                    'product_id':row[1],
                    'product_name':row[2],
                    'quantity':row[3],
                    'max_checkout_qty':row[4],
                    'price':row[5],
                    'color_name':row[6],
                    'product_img_url':row[7],
                    'reserved_quantity':row[8],
                    'stock_status':row[9],
                    'size_value':row[10],
                    'actual_price':per_item_price,
                    
                    
                
            })
    else:
        error_msg = 'Something Went Wrong'
    current_url = request.get_full_path()
    context = {'current_url': current_url,'query_result':data,'error_msg':error_msg}
    return render(request,"cart_pages/cart.html",context)

#Checkout Page
def checkout(request):
    error_msg = 'No Items Added to checkout'
    customer_id = request.session.get("u_customer_id")
    if customer_id == None:
        error_msg = 'Please Login To Place Order'
        context = {'query_result':[],'error_msg':error_msg}
        return render(request,"checkout_pages/checkout.html",context)
    query = "select cartid,united_armor_cart_tbl.product_id,product_name,quantity,max_checkout_qty,united_armor_cart_tbl.price,color_name,product_img_url,reserved_quantity,stock_status,size_value,actual_price,united_armor_cart_tbl.offer_price,united_armor_cart_tbl.color_id,united_armor_cart_tbl.size_id from vff.united_armor_inventorytbl,vff.united_armor_cart_tbl,vff.united_armor_all_productstbl,vff.united_armor_product_sizestbl,vff.united_armor_product_colorstbl where united_armor_product_sizestbl.sizesid=united_armor_cart_tbl.size_id and united_armor_product_colorstbl.colorsid=united_armor_cart_tbl.color_id and united_armor_product_colorstbl.product_id=united_armor_all_productstbl.productid and united_armor_product_colorstbl.product_id=united_armor_cart_tbl.product_id and united_armor_cart_tbl.product_id=united_armor_all_productstbl.productid and united_armor_inventorytbl.product_id=united_armor_all_productstbl.productid and united_armor_inventorytbl.product_id=united_armor_cart_tbl.product_id and united_armor_inventorytbl.color_id=united_armor_cart_tbl.color_id and united_armor_inventorytbl.size_id=united_armor_cart_tbl.size_id and  customer_id='"+str(customer_id)+"'  order by cartid desc"
    query_result = execute_raw_query(query)
    data = []    
    if not query_result == 500:
        for row in query_result:
            actual_price = row[11]
            offer_price = row[12]
            per_item_price= actual_price
            if offer_price !=0.0 or offer_price !=0:
                per_item_price = offer_price
            data.append({
                    'cart_id':row[0],
                    'product_id':row[1],
                    'product_name':row[2],
                    'quantity':row[3],
                    'max_checkout_qty':row[4],
                    'price':row[5],
                    'color_name':row[6],
                    'product_img_url':row[7],
                    'reserved_quantity':row[8],
                    'stock_status':row[9],
                    'size_value':row[10],
                    'actual_price':per_item_price,
                    'color_id':row[13],
                    'size_id':row[14],
                    
                    
                
            })
        
    else:
        error_msg = 'Something Went Wrong'
    customer_name = ''
    address1 = ''
    address2 = ''
    city_name = ''
    state = ''
    pincode = ''
    mobno = ''
    query = "select customer_name,address,address2,city_name,state,pincode,mobno from vff.united_armor_customertbl where customerid='"+str(customer_id)+"'"
    user_data = execute_raw_query_fetch_one(query)
    if user_data :
        customer_name = user_data[0]
        address1 = user_data[1]
        address2 = user_data[2]
        city_name = user_data[3]
        state = user_data[4]
        pincode = user_data[5]
        mobno = user_data[6]
    else:
        error_msg = 'Something Went Wrong'
    
    current_url = request.get_full_path()
    context = {'current_url': current_url,'query_result':data,'error_msg':error_msg,'customer_name':customer_name,'address1':address1,'address2':address2,'city_name':city_name,'state':state,'pincode':pincode,'mobno':mobno}
    return render(request,"checkout_pages/checkout.html",context)

#To Place Order 
def place_order(request):
    if request.method == "POST":
        payment_id = request.POST.get('payment_id', '-1')
        total_price = request.POST.get('total_amount', '0')

        # Get other form data with default values 'NA'
        full_name = request.POST.get('full_name', 'NA')
        country = request.POST.get('country', 'NA')
        street_address_1 = request.POST.get('street_address_1', 'NA')
        street_address_2 = request.POST.get('street_address_2', 'NA')
        town_city = request.POST.get('town_city', 'NA')
        state_county = request.POST.get('state_county', 'NA')
        postcode_zip = request.POST.get('postcode_zip', '-1')
        phone = request.POST.get('phone', '-1')
        order_notes = request.POST.get('order_notes', 'NA')
        cart_ids = request.POST.get('cart_ids', '').split(',')  # Assuming it's a comma-separated list
        product_ids = request.POST.get('product_ids', '').split(',')
        color_ids = request.POST.get('color_ids', '').split(',')
        size_ids = request.POST.get('size_ids', '').split(',')
        quantities = request.POST.get('quantity_list', '').split(',')

        # Handle payment method with default value 'NA'
        payment_method = request.POST.get('payment_method', 'NA')
        payment_status = "Paid"
        if payment_method == "cod":
            payment_status = "Un Paid"
        try:
            with connection.cursor() as cursor:
                customer_id = request.session.get('u_customer_id')
                
                #Updating Customer Information
                update_query="update vff.united_armor_customertbl set customer_name='"+str(full_name)+"',address='"+str(street_address_1)+"',address2='"+str(street_address_2)+"',city_name='"+str(town_city)+"',state='"+str(state_county)+"',country='"+str(country)+"',mobno='"+str(phone)+"',pincode='"+str(postcode_zip)+"' where customerid='"+str(customer_id)+"'"
                print(f'Updating Customer Details ::{update_query}')
                cursor.execute(update_query)
                
                # Insert into Order Table
                insert_order_query = "insert into vff.united_armor_order_tbl(quantity,purchased_price,customer_id) values ('"+str(len(quantities))+"','"+str(total_price)+"','"+str(customer_id)+"') returning orderid "
                print(f"Order Table Query Insert::{insert_order_query}")
                cursor.execute(insert_order_query)
                order_id = cursor.fetchone()[0] 
                
                # Insert Order History Table
                insert_order_history_query = "insert into vff.united_armor_order_historytbl (order_id,status) values ('"+str(order_id)+"','Order Placed')"
                print(f"History Order Table Query Insert::{insert_order_history_query}")
                cursor.execute(insert_order_history_query)
                
                #Payment Table
                update_query="insert into vff.united_armor_paymenttbl(order_id,status,payment_method,razor_pay_id,amount_paid) values ('"+str(order_id)+"','"+str(payment_status)+"','"+str(payment_method)+"','"+str(payment_id)+"','"+str(total_price)+"')"
                print(f'Updating Customer Details ::{update_query}')
                cursor.execute(update_query)
                
                # Insert Into Active Orders Table
                insert_active_orders_query = f"""
                INSERT INTO vff.united_armor_active_orders_tbl (product_id, quantity, customer_id, price, color_id, size_id, offer_price, actual_price, product_img_url, order_id)
                SELECT product_id, quantity, customer_id, price, color_id, size_id, offer_price, actual_price, product_img_url, {order_id}
                FROM vff.united_armor_cart_tbl
                WHERE customer_id = '{customer_id}';
                """
                print(f"Active Order Table Query Insert::{insert_active_orders_query}")
                cursor.execute(insert_active_orders_query)
                
                #To Delete the Entries from Cart Table 
                for cart_id in cart_ids:
                    delete_cart_rows_query = f"""
                        DELETE FROM vff.united_armor_cart_tbl
                        WHERE customer_id = '{customer_id}' AND cartid = '{cart_id}';
                    """
                    print(f'delete_cart_rows_query:{delete_cart_rows_query}')
                    # Execute the delete query for each cart id
                    cursor.execute(delete_cart_rows_query)
                    
                #To Update the Inventory Table 
                for product_id, size_id, color_id, quantity in zip(product_ids, size_ids, color_ids,quantities):
                    update_query = f"""
                        UPDATE vff.united_armor_inventorytbl
                        SET reserved_quantity = reserved_quantity - {quantity},purchased_quantity= purchased_quantity + {quantity}
                        WHERE product_id = {product_id}
                          AND color_id = {color_id}
                          AND size_id = {size_id}
                          AND reserved_quantity >= {quantity};
                    """
                    cursor.execute(update_query)
                
                connection.commit()
                print("Order Placed Successfully")
                return JsonResponse({'message':'success'})
        except Exception as e:
            print(f"Error loading data: {e}")
        return JsonResponse({'message':'error'})
  
#Contact US
def contact_us(request):
    return render(request,'account_pages/contact_us.html')
  
#About US
def about_us(request):
    return render(request,'account_pages/about_us.html')
  
#My Account
def my_account(request):
    error_msg = 'No Order has been made yet'
    customer_id = request.session.get('u_customer_id')
 
    # query = "select activeid,united_armor_active_orders_tbl.product_id,product_name,quantity,max_checkout_qty,united_armor_active_orders_tbl.price,color_name,product_img_url,reserved_quantity,stock_status,size_value,actual_price,united_armor_active_orders_tbl.offer_price,united_armor_active_orders_tbl.color_id,united_armor_active_orders_tbl.size_id,order_id from vff.united_armor_inventorytbl,vff.united_armor_active_orders_tbl,vff.united_armor_all_productstbl,vff.united_armor_product_sizestbl,vff.united_armor_product_colorstbl where united_armor_product_sizestbl.sizesid=united_armor_active_orders_tbl.size_id and united_armor_product_colorstbl.colorsid=united_armor_active_orders_tbl.color_id and united_armor_product_colorstbl.product_id=united_armor_all_productstbl.productid and united_armor_product_colorstbl.product_id=united_armor_active_orders_tbl.product_id and united_armor_active_orders_tbl.product_id=united_armor_all_productstbl.productid and united_armor_inventorytbl.product_id=united_armor_all_productstbl.productid and united_armor_inventorytbl.product_id=united_armor_active_orders_tbl.product_id and united_armor_inventorytbl.color_id=united_armor_active_orders_tbl.color_id and united_armor_inventorytbl.size_id=united_armor_active_orders_tbl.size_id and  customer_id='"+str(customer_id)+"'  order by activeid desc"
    # query = "select activeid,united_armor_active_orders_tbl.product_id,product_name,united_armor_active_orders_tbl.quantity,max_checkout_qty,united_armor_active_orders_tbl.price,color_name,product_img_url,reserved_quantity,stock_status,size_value,actual_price,united_armor_active_orders_tbl.offer_price,united_armor_active_orders_tbl.color_id,united_armor_active_orders_tbl.size_id,order_id,order_status,order_delivered,purchased_date,purchased_time from vff.united_armor_order_tbl,vff.united_armor_inventorytbl,vff.united_armor_active_orders_tbl,vff.united_armor_all_productstbl,vff.united_armor_product_sizestbl,vff.united_armor_product_colorstbl where united_armor_product_sizestbl.sizesid=united_armor_active_orders_tbl.size_id and united_armor_product_colorstbl.colorsid=united_armor_active_orders_tbl.color_id and united_armor_product_colorstbl.product_id=united_armor_all_productstbl.productid and united_armor_product_colorstbl.product_id=united_armor_active_orders_tbl.product_id and united_armor_active_orders_tbl.product_id=united_armor_all_productstbl.productid and united_armor_inventorytbl.product_id=united_armor_all_productstbl.productid and united_armor_inventorytbl.product_id=united_armor_active_orders_tbl.product_id and united_armor_inventorytbl.color_id=united_armor_active_orders_tbl.color_id and united_armor_inventorytbl.size_id=united_armor_active_orders_tbl.size_id and united_armor_order_tbl.orderid=united_armor_active_orders_tbl.order_id and united_armor_order_tbl.customer_id=united_armor_active_orders_tbl.customer_id  and  united_armor_active_orders_tbl.customer_id='"+str(customer_id)+"'  order by activeid desc"
    query = "select activeid,united_armor_active_orders_tbl.product_id,product_name,united_armor_active_orders_tbl.quantity,max_checkout_qty,united_armor_active_orders_tbl.price,color_name,product_img_url,reserved_quantity,stock_status,size_value,actual_price,united_armor_active_orders_tbl.offer_price,united_armor_active_orders_tbl.color_id,united_armor_active_orders_tbl.size_id,order_id,order_current_status,order_delivered,purchased_date,purchased_time,cancelled,cancel_reason,feedback from vff.united_armor_order_tbl,vff.united_armor_inventorytbl,vff.united_armor_active_orders_tbl,vff.united_armor_all_productstbl,vff.united_armor_product_sizestbl,vff.united_armor_product_colorstbl where united_armor_product_sizestbl.sizesid=united_armor_active_orders_tbl.size_id and united_armor_product_colorstbl.colorsid=united_armor_active_orders_tbl.color_id and united_armor_product_colorstbl.product_id=united_armor_all_productstbl.productid and united_armor_product_colorstbl.product_id=united_armor_active_orders_tbl.product_id and united_armor_active_orders_tbl.product_id=united_armor_all_productstbl.productid and united_armor_inventorytbl.product_id=united_armor_all_productstbl.productid and united_armor_inventorytbl.product_id=united_armor_active_orders_tbl.product_id and united_armor_inventorytbl.color_id=united_armor_active_orders_tbl.color_id and united_armor_inventorytbl.size_id=united_armor_active_orders_tbl.size_id and united_armor_order_tbl.orderid=united_armor_active_orders_tbl.order_id and united_armor_order_tbl.customer_id=united_armor_active_orders_tbl.customer_id  and  united_armor_active_orders_tbl.customer_id='"+str(customer_id)+"' order by activeid desc"
    query_result = execute_raw_query(query)
    data = []    
    if not query_result == 500:
        for row in query_result:
            actual_price = row[11]
            offer_price = row[12]
            per_item_price= actual_price
            if offer_price !=0.0 or offer_price !=0:
                per_item_price = offer_price
            data.append({
                    'active_id':row[0],
                    'product_id':row[1],
                    'product_name':row[2],
                    'quantity':row[3],
                    'max_checkout_qty':row[4],
                    'price':row[5],
                    'color_name':row[6],
                    'product_img_url':row[7],
                    'reserved_quantity':row[8],
                    'stock_status':row[9],
                    'size_value':row[10],
                    'actual_price':per_item_price,
                    'color_id':row[13],
                    'size_id':row[14],
                    'order_id':row[15],
                    'order_status':row[16],
                    'order_order_deliveredid':row[17],
                    'purchased_date':row[18],
                    'purchased_time':row[19],
                    'cancelled':row[20],
                    'cancel_reason':row[21],
                    'feedback':row[22],
                    
                    
                
            })
        
    else:
        error_msg = 'Something Went Wrong'
        
    customer_name = ''
    address1 = ''
    address2 = ''
    city_name = ''
    state = ''
    pincode = ''
    mobno = ''
    email = ''
    password = ''
    query = "select customer_name,address,address2,city_name,state,pincode,mobno,email,password from vff.united_armor_customertbl where customerid='"+str(customer_id)+"'"
    user_data = execute_raw_query_fetch_one(query)
    if user_data :
        customer_name = user_data[0]
        address1 = user_data[1]
        address2 = user_data[2]
        city_name = user_data[3]
        state = user_data[4]
        pincode = user_data[5]
        mobno = user_data[6]
        email = user_data[7]
        password = user_data[8]
    else:
        error_msg = 'Something Went Wrong'
    current_url = request.get_full_path()
    context = {'current_url': current_url,'query_result':data,'error_msg':error_msg,'email':email,'password':password,'customer_name':customer_name,'address1':address1,'address2':address2,'city_name':city_name,'state':state,'pincode':pincode,'mobno':mobno}
    return render(request,'account_pages/my_account.html',context)


#Updateing Billing Address 
def update_billing_address(request):
    if request.method == "POST":
        full_name = request.POST.get('full_name', 'NA')
        country = request.POST.get('country', 'NA')
        street_address_1 = request.POST.get('street_address_1', 'NA')
        street_address_2 = request.POST.get('street_address_2', 'NA')
        town_city = request.POST.get('town_city', 'NA')
        state_county = request.POST.get('state_county', 'NA')
        postcode_zip = request.POST.get('postcode_zip', '-1')
        phone = request.POST.get('phone', '-1')
        try:
            with connection.cursor() as cursor:
                customer_id = request.session.get('u_customer_id')
                
                #Updating Customer Information
                update_query="update vff.united_armor_customertbl set customer_name='"+str(full_name)+"',address='"+str(street_address_1)+"',address2='"+str(street_address_2)+"',city_name='"+str(town_city)+"',state='"+str(state_county)+"',country='"+str(country)+"',mobno='"+str(phone)+"',pincode='"+str(postcode_zip)+"' where customerid='"+str(customer_id)+"'"
                print(f'Updating Customer Details ::{update_query}')
                cursor.execute(update_query)
                
                connection.commit()
                print("Billing Address Details Updated Successfully.")
                return JsonResponse({'message':'success'})
        except Exception as e:
            print(f"Error loading data: {e}")
    return JsonResponse({'message':'error'})

#Updateing Account Details
def update_account_details(request):
    if request.method == "POST":
        full_name = request.POST.get('full_name', 'NA')
        email = request.POST.get('email', 'NA')
        current_password = request.POST.get('current_password', 'NA')
        confirm_new_password = request.POST.get('confirm_new_password', '')
        password = current_password
        if not confirm_new_password:
            password = current_password
        try:
            with connection.cursor() as cursor:
                customer_id = request.session.get('u_customer_id')
                
                #Updating Customer Information
                update_query="update vff.united_armor_customertbl set customer_name='"+str(full_name)+"',email='"+str(email)+"',password='"+str(password)+"' where customerid='"+str(customer_id)+"'"
                print(f'Updating Customer Details ::{update_query}')
                cursor.execute(update_query)
                
                connection.commit()
                print("Account Details Updated Successfully.")
                return JsonResponse({'message':'success'})
        except Exception as e:
            print(f"Error loading data: {e}")
    return JsonResponse({'message':'error'})

#Privacy Policy
def privacy_policy(request):
    return render(request,'privacy_pages/privacy_policy.html')  
  
#Terms of use
def terms_of_use(request):
    return render(request,'privacy_pages/terms_of_use.html')  

#Delete From Wish List 
def logout(request):
    if request.method == "POST":
        request.session['u_customer_id'] = None
        request.session['customer_name'] = None
        print("User Logged Out Successfully.")
        return JsonResponse({'message':'Success'})
    
    return JsonResponse({'message':'Oops Something Went Wrong'})



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
# def add_to_cart(request,product_id,color_id,size_id,price,quantity,offer_price):
#     # Convert path parameters to float
#     price = float(price)
#     offer_price = float(offer_price)
#     actual_price = price
#     #If he is a guest user then the customer id will be 1000000
#     customer_id = request.session.get('u_customer_id')
#     if customer_id == '' or customer_id == None:
#         customer_id = 1000000
#     try:
#         with connection.cursor() as cursor:
#             if offer_price != 0.0:
#                 price = offer_price
#             # Adding Item to Cart
#             insert_query = "insert into vff.united_armor_cart_tbl(product_id,customer_id,price,color_id,size_id,quantity,offer_price,actual_price) values ('"+str(product_id)+"','"+str(customer_id)+"','"+str(price)+"','"+str(color_id)+"','"+str(size_id)+"','"+str(quantity)+"','"+str(offer_price)+"','"+str(actual_price)+"')"
            
#             print(f"adding to cart Id::{insert_query}")
#             cursor.execute(insert_query)
#             connection.commit()
#             print("Item Added To Cart Successfully.")
#             return JsonResponse({'message':'Item Added to cart successfully'})
#     except Exception as e:
#         print(f"Error loading data: {e}")
#     return JsonResponse({'message':'Oops Something Went Wrong'})

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


