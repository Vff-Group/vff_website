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
    
    #Update Laundry Customer Token
    path('update_user_device_token/', views.update_user_device_token,name='update_user_device_token'),
    
    #Delivery Boy Login
    path('delivery_boy_login/', views.delivery_boy_login,name='delivery_boy_login'),
    
    #New Order Pickup Request
    path('load_new_orders_requested_to_delivery_boy/', views.load_new_orders_requested_to_delivery_boy,name='load_new_orders_requested_to_delivery_boy'),
    
    #Accept or Reject New Pick Request
    path('accept_or_reject_order_delivery_boy/', views.accept_or_reject_order_delivery_boy,name='accept_or_reject_order_delivery_boy'),
    
    #New Order By customer
    path('load_customer_new_orders/', views.load_customer_new_orders,name='load_customer_new_orders'),
    
    #Active Order for Customer
    path('load_customer_active_order_details/', views.load_customer_active_order_details,name='load_customer_active_order_details'),
    
    #Selected Items Load
    path('load_selected_order_items_order_detail/', views.load_selected_order_items_order_detail,name='load_selected_order_items_order_detail'),
    
    #Load category Wise Details
    path('load_category_wise_details/', views.load_category_wise_details,name='load_category_wise_details'),
    
    #Load Sub Category Details
    path('load_sub_category_wise_details/', views.load_sub_category_wise_details,name='load_sub_category_wise_details'),
    
    #AddLaundry Item to cart
    path('add_laundry_items_to_cart/', views.add_laundry_items_to_cart,name='add_laundry_items_to_cart'),
    
    #Load Cart Details
    path('load_cart_items_selected/', views.load_cart_items_selected,name='load_cart_items_selected'),
    
    #Delete Cart Items
    path('delete_laundry_cart_item/', views.delete_laundry_cart_item,name='delete_laundry_cart_item'),
    
    #Load Extra Items Details
    path('load_extra_items_details/', views.load_extra_items_details,name='load_extra_items_details'),
    
    #Place Order 
    path('place_order_laundry/', views.place_order_laundry,name='place_order_laundry'),
    
    #Load Sub Category Wise Details
    path('load_sub_category_section_wise_details/', views.load_sub_category_section_wise_details,name='load_sub_category_section_wise_details'),
    
    #Cancel Booking
    path('cancel_laundry_order/', views.cancel_laundry_order,name='cancel_laundry_order'),
    
    #Feedback for Order
    path('feedback_laundry_order/', views.feedback_laundry_order,name='feedback_laundry_order'),
    
    #Load All Orders Tab Details
    path('load_all_orders_tab_details/', views.load_all_orders_tab_details,name='load_all_orders_tab_details'),
    
    #Marking Delivery Boy as he is Online
    path('mark_delivery_boy_as_online/', views.mark_delivery_boy_as_online,name='mark_delivery_boy_as_online'),
    
    #Delivery Boy All Orders
    path('load_delivery_boy_all_orders_tab_details/', views.load_delivery_boy_all_orders_tab_details,name='load_delivery_boy_all_orders_tab_details'),
    
    #Active Orders for Delivery Boy
    path('delivery_boycurrent_active_order_details/', views.delivery_boycurrent_active_order_details,name='delivery_boycurrent_active_order_details'),
    
    #Updating Order Status
    path('update_current_order_status/', views.update_current_order_status,name='update_current_order_status'),
    
    #Load Today Notification
    path('load_todays_notifications/', views.load_todays_notifications,name='load_todays_notifications'),
    
    #Delivery Boy Stats
    path('delivery_boy_stats/', views.delivery_boy_stats,name='delivery_boy_stats'),
    
    #Load All Branches
    path('load_all_branches/', views.load_all_branches,name='load_all_branches'),
    
    #Load All Pickup Order
    path('load_all_pickup_order/', views.load_all_pickup_order,name='load_all_pickup_order'),
    
    #Load All Drop Order
    path('load_all_drop_order/', views.load_all_drop_order,name='load_all_drop_order'),
    
    #Load all pickup or drop booking details
    path('load_all_pickup_or_drop_booking_details/', views.load_all_pickup_or_drop_booking_details,name='load_all_pickup_or_drop_booking_details'),
    
    #load all offers
    path('load_all_offers/', views.load_all_offers,name='load_all_offers'),
    
    #UPdate Current New Booking Status
    path('update_current_new_booking_status/', views.update_current_new_booking_status,name='update_current_new_booking_status'),
    
    
    
    
    
    

]