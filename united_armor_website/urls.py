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
    
    #Single Product Details
    path('product/',views.product,name='product'),
   
    #Cart
    path('cart/',views.cart_details,name='cart'),
   
    #Checkout Page
    path('checkout/',views.checkout,name='checkout'),
   
    
    
    
   
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
