from django.urls import path
from . import views

app_name = 'laundry_mobile_app' #namespace

urlpatterns = [
    #  path('get_csrf_token/', views.get_csrf_token, name='get_csrf_token'),
    
    #Login
    path('login/', views.login,name='login'),
    
    
    
    

]