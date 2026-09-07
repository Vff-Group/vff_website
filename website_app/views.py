
from django.core.mail import send_mail
from django.core.mail import EmailMessage
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
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
import os
from django.conf import settings
from django.http import JsonResponse
# Create your views here.
def index(request):
    current_url = request.get_full_path()
    return render(request,"index.html",{'current_url': current_url})

def about_us(request):
    current_url = request.get_full_path()
    return render(request,"about_us.html",{'current_url': current_url})

def services(request):
    current_url = request.get_full_path()
    return render(request,"services.html",{'current_url': current_url})

def boutique(request):
    current_url = request.get_full_path()
    return render(request,"boutique.html",{'current_url': current_url})

def franchise(request):
    current_url = request.get_full_path()
    return render(request,"franchise.html",{'current_url': current_url})

def contactus(request):
    current_url = request.get_full_path()
    return render(request,"contactus.html",{'current_url': current_url})

def privacy(request):
    current_url = request.get_full_path()
    return render(request,"privacy.html",{'current_url': current_url})

def gym_home(request):
    current_url = request.get_full_path()
    return render(request,"gym_index.html",{'current_url': current_url})

def terms_of_service(request):
    current_url = request.get_full_path()
    return render(request,"terms_of_service.html",{'current_url': current_url})

@csrf_exempt
def contact_form_submit(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        
        message = request.POST.get('w3lMessage')
        print(f'Name: {name}\nEmail: {email}\nMessage: {message}')
        # Send email using configured settings
        EmailMessage(
               f'Name: {name}\nEmail: {email}\nMessage: {message}',
               message,
               email, # Send from (your website)
               ['info@vff-group.com'], # Send to (your admin email)
               [],
               reply_to=[email] # Email from the form to get back to
           ).send()
        # res = send_mail(
        #     'Subject',
        #     f'Name: {name}\nEmail: {email}\nMessage: {message}',
        #     email,  # Replace with your email ID as the sender
        #     ['info@vff-group.com'],  # Replace with the recipient's email
        #     fail_silently=False,
        # )
        print(f'Contact Res::')
        return JsonResponse({'message': 'Message sent successfully'})
    return JsonResponse({'error': 'Invalid request'}, status=400)

def custom_404_view(request, exception=None):
    return render(request, '404.html', status=404)

def custom_500_view(request, exception=None):
    return render(request, '500.html', status=500)

def how_it_works(request):
    current_url = request.get_full_path()
    return render(request, "how_it_works.html", {'current_url': current_url})


def faq(request):
    current_url = request.get_full_path()
    return render(request, "faq.html", {'current_url': current_url})


def book_order_now(request):
    current_url = request.get_full_path()
    if request.method == "POST":
        name = request.POST.get("customer_name")
        address = request.POST.get("address")
        phone_no = request.POST.get("contact_no")
        try:
            with connection.cursor() as cursor:
                insert_query = (
                    "insert into vff.laundry_website_bookingstbl (name,phone_no,address) "
                    "values ('" + str(name) + "','" + str(phone_no) + "','" + str(address) + "')"
                )
                cursor.execute(insert_query)
                connection.commit()
                print("New Website Bookings Done Successfully.")
                return redirect('website_app:index')
        except Exception as e:
            print(f"Error loading data: {e}")
    return render(request, "book_order.html", {'current_url': current_url})


def _normalize_mobile(raw):
    digits = re.sub(r"\D", "", (raw or "").strip())
    if len(digits) > 10 and digits.startswith("91"):
        digits = digits[-10:]
    return digits


def _ensure_deletion_requests_table(cursor):
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS vff.account_deletion_requeststbl (
            id SERIAL PRIMARY KEY,
            usrid INTEGER,
            usrname VARCHAR(255) NOT NULL,
            mobile_no VARCHAR(50) NOT NULL,
            requested_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW(),
            status VARCHAR(50) DEFAULT 'pending'
        )
        """
    )


def delete_account(request):
    current_url = request.get_full_path()
    context = {
        "current_url": current_url,
        "success": False,
        "error": "",
        "username": "",
        "mobile": "",
    }

    if request.method != "POST":
        return render(request, "delete_account.html", context)

    username = (request.POST.get("username") or "").strip()
    mobile = _normalize_mobile(request.POST.get("mobile"))
    context["username"] = username
    context["mobile"] = mobile

    if not username or not mobile:
        context["error"] = "Please enter both username and mobile number."
        return render(request, "delete_account.html", context)

    if len(mobile) != 10:
        context["error"] = "Please enter a valid 10-digit mobile number."
        return render(request, "delete_account.html", context)

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT usrid, usrname, mobile_no
                FROM vff.usertbl
                WHERE LOWER(TRIM(usrname)) = LOWER(%s)
                  AND RIGHT(REGEXP_REPLACE(COALESCE(mobile_no, ''), '[^0-9]', '', 'g'), 10) = %s
                LIMIT 1
                """,
                [username, mobile],
            )
            row = cursor.fetchone()
            if not row:
                context["error"] = "No account found with this username and mobile number."
                return render(request, "delete_account.html", context)

            usrid, db_username, db_mobile = row
            _ensure_deletion_requests_table(cursor)
            cursor.execute(
                """
                INSERT INTO vff.account_deletion_requeststbl (usrid, usrname, mobile_no, status)
                VALUES (%s, %s, %s, 'pending')
                """,
                [usrid, db_username, db_mobile],
            )
            connection.commit()
            print(f"Account deletion requested for usrid={usrid}, username={db_username}")
            context["success"] = True
            context["username"] = ""
            context["mobile"] = ""
    except Exception as e:
        print(f"Error processing account deletion request: {e}")
        context["error"] = "Something went wrong. Please try again later or contact support."

    return render(request, "delete_account.html", context)
