from django.urls import path
from . import views

app_name = 'clothing_app' #namespace

urlpatterns = [
    #  path('get_csrf_token/', views.get_csrf_token, name='get_csrf_token'),
    
    #Login
    path('login/', views.login,name='login'),
    
    #register
    path('register/', views.new_register,name='register'),
    
    #Update Notification Device Token
    path('update_device_token/', views.update_device_token,name='update_device_token'),
    
    #Loads the main Categories Like Men,Women
    path('get_main_categories/', views.get_main_categories,name='get_main_categories'),
    
    #To Get Categories Like Shop By Category, Shop By Sports
    path('get_categories/', views.get_categories,name='get_categories'),
    
    #To Get Sub Categories Like Top,Jackets based on Category ID
    path('get_sub_categories/', views.get_sub_categories,name='get_sub_categories'),
    
    #To Load Product Category all filters Like Clothing, Accessories
    path('get_product_category_filter/', views.get_product_category_filter,name='get_product_category_filter'),
    
    #To Load Product Type all Filters Like Tops,etc
    path('get_product_type_filter/', views.get_product_type_filter,name='get_product_type_filter'),
    
    #To Load Single Product Details
    path('load_single_product_details/', views.load_single_product_details,name='load_single_product_details'),
    
    #To Load All Product Details
    path('load_all_product_details/', views.load_all_product_details,name='load_all_product_details'),
    
    #To Load Single Product Image Details
    path('get_product_images/', views.get_product_images,name='get_product_images'),
    
    #To Load Single Product Color Details
    path('get_product_colors/', views.get_product_colors,name='get_product_colors'),
    
    #To Load App Home Page Main Categories
    path('get_home_main_categories/', views.get_home_main_categories,name='get_home_main_categories'),
    
    #addto wishlistt
    path('add_to_wishlist/', views.add_to_wishlist,name='add_to_wishlist'),
    
    #remove from wishlist
    path('delete_from_wishlist/', views.delete_from_wishlist,name='delete_from_wishlist'),
    
    #get all filter data
    path('get_all_filters/', views.get_all_filters,name='get_all_filters'),
    
    

]