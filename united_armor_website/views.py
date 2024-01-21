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
    query_product = "SELECT productid,product_name,fitting_type,fitting_id,main_title_name,cat_name,sub_cat_name,product_catid,product_category_name,united_armor_all_productstbl.product_type_id,product_type_name,price,united_armor_all_productstbl.main_cat_id,united_armor_all_productstbl.cat_id,united_armor_all_productstbl.sub_catid,offer_price,default_images,default_size,ratings,default_color_id,color_name,color_code FROM vff.united_armor_product_colorstbl,vff.united_armor_all_productstbl,vff.united_armor_product_categorytbl,vff.united_armor_product_typetbl,vff.united_armor_main_categorytbl,vff.united_armor_categorytbl,vff.united_armor_sub_categorytbl WHERE united_armor_product_colorstbl.colorsid=default_color_id  AND united_armor_product_categorytbl.product_catid=united_armor_all_productstbl.product_collection_id AND united_armor_product_typetbl.product_type_id=united_armor_all_productstbl.product_type_id AND united_armor_main_categorytbl.main_cat_id=united_armor_all_productstbl.main_cat_id AND united_armor_all_productstbl.cat_id=united_armor_categorytbl.catid AND united_armor_all_productstbl.sub_catid=united_armor_sub_categorytbl.sub_catid AND united_armor_all_productstbl.main_cat_id='"+str(s_main_cat_id)+"' order by productid desc"
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
    query_product = "SELECT productid,product_name,fitting_type,fitting_id,main_title_name,cat_name,sub_cat_name,product_catid,product_category_name,united_armor_all_productstbl.product_type_id,product_type_name,price,united_armor_all_productstbl.main_cat_id,united_armor_all_productstbl.cat_id,united_armor_all_productstbl.sub_catid,offer_price,default_images,default_size,ratings,default_color_id,color_name,color_code FROM vff.united_armor_product_colorstbl,vff.united_armor_all_productstbl,vff.united_armor_product_categorytbl,vff.united_armor_product_typetbl,vff.united_armor_main_categorytbl,vff.united_armor_categorytbl,vff.united_armor_sub_categorytbl WHERE united_armor_product_colorstbl.colorsid=default_color_id  AND united_armor_product_categorytbl.product_catid=united_armor_all_productstbl.product_collection_id AND united_armor_product_typetbl.product_type_id=united_armor_all_productstbl.product_type_id AND united_armor_main_categorytbl.main_cat_id=united_armor_all_productstbl.main_cat_id AND united_armor_all_productstbl.cat_id=united_armor_categorytbl.catid AND united_armor_all_productstbl.sub_catid=united_armor_sub_categorytbl.sub_catid AND united_armor_all_productstbl.sub_catid='"+str(s_sub_cat_id)+"' order by productid desc"
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
def product(request):
    current_url = request.get_full_path()
    return render(request,"product_pages/single_product.html",{'current_url': current_url})

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
    return JsonResponse({'ErrorCode#8': 'ErrorCode#8'})


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
