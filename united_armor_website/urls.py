from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static



app_name = 'united_armor' #nameSpaceses

urlpatterns = [
    #Coming Soon Page
    # path('home',views.coming_soon,name='coming_soon'),
    
    #Login
    path('login/',views.handle_login,name='login'),
    
    #Register
    path('register/',views.handle_register,name='register'),
    
    #Home
    path('home/',views.home,name='home'),
    
    #All Products
    path('all_products/',views.all_products,name='all_products'),
    
    #All Products With Main Cat ID
    path('all_products/<int:s_main_cat_id>/<str:s_main_cat_name>/',views.all_products_with_main_category,name='all_products_with_main_category'),
    
    #All Products With Main Cat ID and Category ID
    path('all_products/<int:s_main_cat_id>/<str:s_main_cat_name>/<int:s_cat_id>/<str:s_cat_name>/',views.all_products_with_category,name='all_products_with_category'),
    
    #All Products With Main Cat ID , Category ID , Sub Category ID
    path('all_products/<int:s_main_cat_id>/<str:s_main_cat_name>/<int:s_cat_id>/<str:s_cat_name>/<int:s_sub_cat_id>/<str:s_sub_cat_name>/',views.all_products_with_sub_category,name='all_products_with_sub_category'),
    
    #Single Product Details
    path('product/<int:product_id>/',views.product,name='product'),
   
    #Wish list
    path('wishlist/',views.wishlist_details,name='wishlist'),
   
    # Delete From Wish list
    path('delete_from_wishlist/<int:wishlist_id>/',views.delete_from_wishlist,name='delete_from_wishlist'),
    
    
    #Cart
    path('cart/',views.cart_details,name='cart'),
    
    # Add To Cart
    path('add_to_cart/',views.add_to_cart,name='add_to_cart'),
    
    # Update Cart
    path('update_cart/',views.update_cart,name='update_cart'),
    
    # Remove From Cart
    path('remove_cart_item/',views.remove_cart_item,name='remove_cart_item'),
   
    #Checkout Page
    path('checkout/',views.checkout,name='checkout'),
   
    #Checkout Page
    path('place_order/',views.place_order,name='place_order'),
   
    #My Account
    path('account/',views.my_account,name='account'),
   
    #My Account
    path('my_orders/',views.my_orders,name='my_orders'),
   
    #Privacy Policy
    path('privacy_policy/',views.privacy_policy,name='privacy_policy'),
   
    #Terms of Use
    path('terms_of_use/',views.terms_of_use,name='terms_of_use'),
   
    #Contact Us
    path('contact_us/',views.contact_us,name='contact_us'),
   
    #About Us
    path('about_us/',views.about_us,name='about_us'),
   
    #Update billing address
    path('update_billing_address/',views.update_billing_address,name='update_billing_address'),
   
    #Update Account Details
    path('update_account_details/',views.update_account_details,name='update_account_details'),
   
    #Handling Cancel , Return and Feedback
    path('handle_cancel_return_feedback/',views.handle_cancel_return_feedback,name='handle_cancel_return_feedback'),
   
    #Log Out
    path('logout/',views.logout,name='logout'),
    
    # Add Item to Cart
    path('add_to_cart/<int:product_id>/<int:color_id>/<int:size_id>/<path:price>/<int:quantity>/<path:offer_price>/',views.add_to_cart,name='add_to_cart'),
    
    # Add Item to Wishlist
    path('add_to_wishlist/<int:product_id>/<int:color_id>/',views.add_to_wishlist,name='add_to_wishlist'),
   
    
    
    
   
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
