from django.urls import path
from . import views

app_name = 'laundry_mobile_app' #namespace

urlpatterns = [
    #  path('get_csrf_token/', views.get_csrf_token, name='get_csrf_token'),
    
    #Login
    path('login/', views.login,name='login'),
    
    #Loading all Categories
    path('load_laundry_all_categories/', views.load_laundry_all_categories,name='load_laundry_all_categories'),
    
    #Loading customer Address
    path('load_laundry_customer_address/', views.load_laundry_customer_address,name='load_laundry_customer_address'),
    
    #Request Pickup Laundry Customer
    path('request_pickup_laundry_customer/', views.request_pickup_laundry_customer,name='request_pickup_laundry_customer'),
    
    
    
    

]