from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

app_name = 'dashboard_app' #nameSpaceses

urlpatterns = [
    path('',views.login_view,name='login'),
    path('all_branches/',views.all_branches,name='all_branches'),
    path('selected_branch/',views.save_selected_branch,name='selected_branches'),
    path('dashboard/',views.dashboard,name='dashboard'),
    path('search/',views.search_orderid_or_mobile_number,name='search'),
    path('customers/',views.all_customers,name='customers'),
    path('customers/add_customer/',views.add_customer,name='add_customer'),
    path('customers/update_customer/<int:usrid>',views.add_customer,name='update_customer'),
    path('delivery_agents/',views.all_delivery_agents,name='delivery_agents'),
    path('delivery_agents/add_delivery_agent/',views.add_delivery_agent,name='add_delivery_agent'),
    path('delivery_agents/add_delivery_agent/<int:usrid>',views.add_delivery_agent,name='update_delivery_agent'),
    path('all_orders/',views.all_orders,name='all_orders'),
    path('all_unassigned_orders/',views.all_unassigned_orders,name='all_unassigned_orders'),
    path('all_orders/create_order/',views.create_new_order,name='create_order'),
    path('all_orders/order_details/<int:orderid>',views.view_order_detail,name='view_order_detail'),
    path('assigned_delivery_boy/<int:orderid>',views.assigned_delivery_boy,name='assigned_delivery_boy'),
    path('delivery_accept/<int:orderid>/<int:delivery_boy_id>',views.delivery_accept,name='delivery_accept'),
    path('update_order_status/<int:order_id>',views.update_order_status,name='update_order_status'),
    path('categories/',views.all_categories,name='all_categories'),
    path('categories/add_category/',views.add_category,name='add_category'),
    path('categories/update_category_details/<int:catid>',views.add_category,name='update_category'),
    path('sub_categories/<int:catid>/<str:catname>',views.all_sub_categories,name='all_sub_categories'),
    path('sub_categories/add_sub_category/<int:catid>/<str:catname>',views.add_sub_category,name='add_sub_category'),
    path('sub_categories/update_sub_category_details/<int:catid>/<int:subcatid>/<str:catname>',views.update_sub_category,name='update_sub_category'),
    
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
