
from django.core.mail import send_mail
from django.core.mail import EmailMessage
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render,redirect, reverse
from django.db import connection, DatabaseError
from django.views.decorators.cache import never_cache
from django.contrib.auth import logout
from django.http import HttpResponseServerError,JsonResponse,HttpResponse,HttpResponseRedirect,FileResponse,Http404
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


def our_team(request):
    current_url = request.get_full_path()
    return render(request, "our_team.html", {'current_url': current_url})


TEAM_ASSET_FILES = {
    "our-team.css": ("css", "our-team.css"),
    "david-muller.jpeg": ("images/our_partners", "david-muller.jpeg"),
    "saurabh-goswami.jpeg": ("images/our_partners", "saurabh-goswami.jpeg"),
    "sham-gaonkar.jpeg": ("images/our_partners", "sham-gaonkar.jpeg"),
    "srinivas-paladi.png": ("images/our_partners", "srinivas-paladi.png"),
    "uday.png": ("images/our_partners", "uday.png"),
    "madhav-pejoli.jpeg": ("images/our_partners", "madhav-pejoli.jpeg"),
    "laxmi-zazari.png": ("images/our_partners", "laxmi-zazari.png"),
    "mohammed-shaheed-maniyar.png": ("images/our_partners", "mohammed-shaheed-maniyar.png"),
    "harmeet-singh.jpg": ("images/our_partners", "harmeet-singh.jpg"),
}


def serve_team_asset(request, filename):
    """Serve team photos/CSS from app static so nginx /static 404s do not break Our Team."""
    filename = os.path.basename(filename)
    spec = TEAM_ASSET_FILES.get(filename)
    if not spec:
        raise Http404()
    rel_dir, name = spec
    for root in (
        os.path.join(settings.BASE_DIR, "website_app", "static"),
        os.path.join(settings.BASE_DIR, "static"),
    ):
        path = os.path.join(root, rel_dir, name)
        if os.path.isfile(path):
            content_type, _ = mimetypes.guess_type(path)
            return FileResponse(open(path, "rb"), content_type=content_type or "application/octet-stream")
    raise Http404()


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


def delete_account(request):
    """Show delete form. On valid username+mobile, only show a message — never delete the account."""
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
                SELECT usrid
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

            # Intentionally do not delete or modify the account — message only.
            context["success"] = True
            context["username"] = ""
            context["mobile"] = ""
    except Exception as e:
        print(f"Error validating account deletion form: {e}")
        context["error"] = "Something went wrong. Please try again later or contact support."

    return render(request, "delete_account.html", context)
