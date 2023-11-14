from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

app_name = 'dashboard_app' #nameSpacese

urlpatterns = [
    path('',views.login_view,name='login'),
    path('all_branches/',views.all_branches,name='all_branches'),
    path('selected_branch/',views.save_selected_branch,name='selected_branches'),
    path('dashboard/',views.dashboard,name='dashboard'),
    path('search/',views.search_orderid_or_mobile_number,name='search'),
    path('customers/',views.all_customers,name='customers'),
    path('customers/add_customer/',views.add_customer,name='add_customer'),
    path('customers/delete_customer/<int:usrid>',views.delete_customer,name='delete_customer'),
    path('customers/update_customer/<int:usrid>',views.add_customer,name='update_customer'),
    path('delivery_agents/',views.all_delivery_agents,name='delivery_agents'),
    path('delivery_agents/add_delivery_agent/',views.add_delivery_agent,name='add_delivery_agent'),
    path('delivery_agents/add_delivery_agent/<int:usrid>',views.add_delivery_agent,name='update_delivery_agent'),
    path('delivery_agents/delete_delivery_agent/<int:usrid>',views.delete_delivery_boy,name='delete_delivery_boy'),
    path('all_orders/',views.all_orders,name='all_orders'),
    # path('all_unassigned_orders/',views.all_unassigned_orders,name='all_unassigned_orders'),
    path('all_unassigned_bookings/',views.all_unassigned_bookings,name='all_unassigned_bookings'),
    path('all_bookings/',views.all_bookings,name='all_bookings'),
    path('all_orders/create_order/',views.create_new_order,name='create_order'),
    path('all_orders/order_details/<int:orderid>',views.view_order_detail,name='view_order_detail'),
    path('all_orders/generate_bill/<int:orderid>',views.generate_bill,name='generate_bill'),
    path('all_orders/print_label_tags/<int:orderid>',views.print_label_tags,name='print_label_tags'),
    path('assigned_delivery_boy/<int:orderid>',views.assigned_delivery_boy,name='assigned_delivery_boy'),
    path('delivery_accept/<int:booking_id>/<int:delivery_boy_id>',views.delivery_accept,name='delivery_accept'),
    path('update_order_status/<int:order_id>/<int:booking_id>',views.update_order_status,name='update_order_status'),
    path('categories/',views.all_categories,name='all_categories'),
    path('categories/add_category/',views.add_category,name='add_category'),
    path('categories/update_category_details/<int:catid>',views.add_category,name='update_category'),
    path('sub_categories/<int:catid>/<str:catname>',views.all_sub_categories,name='all_sub_categories'),
    path('sub_categories/add_sub_category/<int:catid>/<str:catname>',views.add_sub_category,name='add_sub_category'),
    path('sub_categories/update_sub_category_details/<int:catid>/<int:subcatid>/<str:catname>',views.update_sub_category,name='update_sub_category'),
    
    #Staff Laundry
    path('staff/add_staff/',views.add_staff,name='add_staff'),
    path('staff/update_staff/<int:usrid>',views.add_staff,name='update_staff'),
    path('staff/',views.all_staff,name='all_staff'),
    
    
    
    #Expenses Laundry
    path('all_expenses/',views.all_expenses,name='all_expenses'),
    path('all_expenses/add_expense_new_item/',views.add_expense_new_item,name='add_expense_new_item'),
    
    #Expense Category Routes
    path('expense_category/',views.expense_category,name='expense_category'),
    path('expense_category/add_expense_category/',views.add_expense_category,name='add_expense_category'),
    
    #Branch details Routes
    path('all_main_branches/',views.all_main_branches,name='all_main_branches'),
    path('all_main_branches/add_branch_details/',views.add_new_branch,name='add_branch_details'),
    path('all_main_branches/update_branch_details/<int:branch_id>/<int:usr_id>/',views.add_new_branch,name='update_branch_details'),
    
    #Order Screens
    path('order_status_screen/',views.order_status_screen,name='order_status_screen'),
    path('counter_orders_screen/',views.counter_orders_screen,name='counter_orders_screen'),
    path('load_sub_categories/<str:cat_id>',views.load_sub_categories,name='load_sub_categories'),
    path('load_other_category_wise_details/<str:cat_id>',views.load_other_category_wise_details,name='load_other_category_wise_details'),
    path('load_section_type_sub_categories/<str:section_type>',views.load_section_type_sub_categories,name='load_section_type_sub_categories'),
    path('search_customer_to_assign_order/<str:mobno>/',views.search_customer_to_assign_order,name='search_customer_to_assign_order'),
    
    #Add Items TO Cart
    path('add_items_to_cart/',views.add_items_to_cart,name='add_items_to_cart'),
    #Generate Booking ID
    path('generate_booking_id/',views.generate_booking_id,name='generate_booking_id'),
    #Delete Cart Item
    path('delete_cart_item/',views.delete_cart_item,name='delete_cart_item'),
    #Reload Cart Item
    path('load_cart_items_after_deletion/',views.load_cart_items_after_deletion,name='load_cart_items_after_deletion'),
    #Load extra Add ons
    path('load_extra_items/',views.load_extra_items,name='load_extra_items'),
    #Place Order
    path('place_new_order/',views.place_new_order,name='place_new_order'),
    
    
    #Reports Screen
    path('daily_report/',views.daily_report,name='daily_report'),
    path('order_report/',views.order_report,name='order_report'),
    path('sales_report/',views.sales_report,name='sales_report'),
    path('expense_report/',views.expense_report,name='expense_report'),
    path('tax_report/',views.tax_report,name='tax_report'),
    
    #Payments Screen
    path('payment_receipt/',views.payment_receipt,name='payment_receipt'),
    path('load_payment_receipt/<str:start_date>/<str:end_date>/',views.load_payment_receipt,name='load_payment_receipt'),
 
    #Notification Screen   
    path('get_todays_notification/',views.get_todays_notification,name='get_todays_notification'),
    
    #Load Charts Details 
    path('get_delivery_chart_details/',views.get_delivery_chart_details,name='get_delivery_chart_details'),
    path('get_sales_chart_details/',views.get_sales_chart_details,name='get_sales_chart_details'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
