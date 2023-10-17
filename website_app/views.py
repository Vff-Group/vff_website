from django.shortcuts import render

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

def contactus(request):
    current_url = request.get_full_path()
    return render(request,"contactus.html",{'current_url': current_url})

def privacy(request):
    current_url = request.get_full_path()
    return render(request,"privacy.html",{'current_url': current_url})
