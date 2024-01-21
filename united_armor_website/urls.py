from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static



app_name = 'united_armor' #nameSpaceses

urlpatterns = [
    #Coming Soon Page
    # path('home',views.coming_soon,name='coming_soon'),
    
    #Home
    path('home',views.home,name='home'),
    
    #All Products
    path('all_products/',views.all_products,name='all_products'),
    
    #All Products With Main Cat ID
    path('all_products/<int:s_main_cat_id>/<str:s_main_cat_name>/',views.all_products_with_main_category,name='all_products_with_main_category'),
    
    #All Products With Main Cat ID and Category ID
    path('all_products/<int:s_main_cat_id>/<str:s_main_cat_name>/<int:s_cat_id>/<str:s_cat_name>/',views.all_products_with_category,name='all_products_with_category'),
    
    #All Products With Main Cat ID , Category ID , Sub Category ID
    path('all_products/<int:s_main_cat_id>/<str:s_main_cat_name>/<int:s_cat_id>/<str:s_cat_name>/<int:s_sub_cat_id>/<str:s_sub_cat_name>/',views.all_products_with_sub_category,name='all_products_with_sub_category'),
    
    #Single Product Details
    path('product/',views.product,name='product'),
   
    #Cart
    path('cart/',views.cart_details,name='cart'),
   
    #Checkout Page
    path('checkout/',views.checkout,name='checkout'),
    
    #Main Navbar Categories
    path('get_main_categories/',views.get_main_categories,name='get_main_categories'),
    
    #Categories
    path('get_categories/',views.get_categories,name='get_categories'),
    
    #Get Sub Categories
    path('get_sub_categories/',views.get_sub_categories,name='get_sub_categories'),
   
    
    
    
   
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
