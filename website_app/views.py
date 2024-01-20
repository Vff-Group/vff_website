from django.shortcuts import render
from django.core.mail import send_mail
from django.core.mail import EmailMessage
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
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
