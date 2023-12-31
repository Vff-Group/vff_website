from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

app_name = 'clothing_dashboard_app' #nameSpaceses

urlpatterns = [
    #Login
    path('',views.login_view,name='login'),
   
    #Dashboard
    path('dashboard/',views.dashboard_view,name='dashboard'),
   
    #All Customers
    path('all_customers/',views.all_customers,name='all_customers'),
   
    #All Main Categories
    path('all_main_categories/',views.all_main_categories,name='all_main_categories'),
   
    #All Categories
    path('all_categories/<int:main_cat_id>/<str:main_cat_name>/',views.all_categories,name='all_categories'),
   
    #All Sub Categories
    path('all_sub_categories/<int:main_cat_id>/<str:main_cat_name>/<int:cat_id>/<str:cat_name>/',views.all_sub_categories,name='all_sub_categories'),
   
    #All Products
    path('all_products/<int:main_cat_id>/<int:cat_id>/<int:sub_cat_id>/',views.all_products_details,name='all_products'),
   
    #Add New Products
    path('add_new_product/',views.add_new_product,name='add_new_product'),
   
    #Update Main Category Details
    path('update_main_category_details/',views.update_main_category_details,name='update_main_category_details'),
   
    #Update Category Details
    path('update_category_details/<int:main_cat_id>/',views.update_category_details,name='update_category_details'),
   
    #Update Sub Category Details
    path('update_sub_category_details/<int:main_cat_id>/<int:cat_id>/',views.update_sub_category_details,name='update_sub_category_details'),
   
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
