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

#Home Page
def home(request):
    current_url = request.get_full_path()
    return render(request,"home_pages/home.html",{'current_url': current_url})

#All Products
def all_products(request):
    current_url = request.get_full_path()
    return render(request,"product_pages/all_products.html",{'current_url': current_url})

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
def custom_404_view_united(request):
    current_url = request.get_full_path()
    return render(request, 'error_pages/404.html', status=404)

#5 0 0 Page
def custom_500_view_united(request):
    current_url = request.get_full_path()
    return render(request, 'error_pages/500.html', status=500)