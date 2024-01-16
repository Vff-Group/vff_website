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
    
    #Home Page All Products
    path('all_products_main/',views.all_products_main,name='all_products_main'),
    
    # Single Product Colors
    path('single_product_colors/<int:main_cat_id>/<int:cat_id>/<int:sub_cat_id>/<int:product_id>/<str:product_name>/',views.single_product_colors,name='single_product_colors'),
   
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
   
    # Add New Products
    path('add_new_product/<int:main_cat_id>/<int:cat_id>/<int:sub_cat_id>/',views.add_new_product,name='add_new_product'),
   
    # Update New Products
    path('update_new_product/<int:main_cat_id>/<int:cat_id>/<int:sub_cat_id>/<int:product_id>/',views.update_new_product,name='update_new_product'),
   
    # Update New Products With Optional For Main Page Products
    path('update_new_product/<int:main_cat_id>/<int:cat_id>/<int:sub_cat_id>/<int:product_id>/<int:ret>/',views.update_new_product,name='update_new_product'),
   
    # View Images of different Colors
    path('view_product_images/<str:product_name>/<str:color_name>/<int:product_id>/<int:color_id>/',views.view_product_images,name='view_product_images'),
   
    # Add more Colors to the product with images
    path('add_new_color_and_image_to_product/<int:main_cat_id>/<int:cat_id>/<int:sub_cat_id>/<int:product_id>/<str:product_name>/',views.add_new_color_and_image_to_product,name='add_new_color_and_image_to_product'),
   
    # Add New Main Category
    path('add_new_main_category/',views.add_new_main_category,name='add_new_main_category'),
   
    #Update Main Category Details
    path('update_main_category_details/',views.update_main_category_details,name='update_main_category_details'),
   
    # Add New  Category
    path('add_new_category/',views.add_new_category,name='add_new_category'),
   
    #Update  Category Details
    path('update_category_details/',views.update_category_details,name='update_category_details'),
   
    # Add New Sub Category
    path('add_new_sub_category/',views.add_new_sub_category,name='add_new_sub_category'),
   
    #Update Sub Category Details
    path('update_sub_category_details/',views.update_sub_category_details,name='update_sub_category_details'),
   
    
   
    #---------------- PRE ORDER Sequence Paths ------------------
    
    #PURCHASE ORDER DETAILS
    path('all_purchase_orders/',views.all_purchase_orders,name='all_purchase_orders'),
    
    # ADD NEW PURCHASE ORDER DETAILS
    path('add_new_purchase_orders/',views.add_new_purchase_orders,name='add_new_purchase_orders'),
    
    # All Supplier
    path('all_suppliers/',views.all_suppliers,name='all_suppliers'),
    
    # Add New Supplier
    path('add_new_supplier/',views.add_new_supplier,name='add_new_supplier'),
    
    # Update Supplier Details
    path('update_supplier_details/',views.update_supplier_details,name='update_supplier_details'),
   
    
    
    #---------------- INVENTORY PART ------------------
    #INVENTORY DASHBOARD
    path('inventory/',views.inventory,name='inventory'),
    
    # Add Product based on color to inventory
    path('add_product_to_inventory/<int:main_cat_id>/<int:cat_id>/<int:sub_cat_id>/<int:product_id>/<str:product_name>/<int:color_id>/',views.add_product_to_inventory,name='add_product_to_inventory'),
    
    # Load all Products to add to inventory to add quantity
    path('attach_to_inventory/',views.attach_to_inventory,name='attach_to_inventory'),
    
    # Load Single Product Sizes Based on ColorID to add initial inventory Stock for Inventory Table
    path('load_add_initial_stock/<int:product_id>/<int:color_id>/<str:color_name>/<str:product_name>/',views.load_add_initial_stock,name='load_add_initial_stock'),
    
    # Load all Products to add to inventory to add quantity
    path('attach_to_inventory_stock/<int:product_id>/<int:color_id>/',views.attach_to_inventory_stock,name='attach_to_inventory_stock'),
    
    # Load all Inventory Products
    path('load_all_inventory_stock_products/',views.load_all_inventory_stock_products,name='load_all_inventory_stock_products'),
    
    # Update Stock Status and Details
    path('update_stock_details/<int:product_id>/<int:size_id>/<int:color_id>/',views.update_stock_details,name='update_stock_details'),
    
   #---------------- ORDERS PART ------------------
    #All ORDERS
    path('all_orders/',views.all_orders,name='all_orders'),
    
    #order details
    path('order_details/<int:order_id>/',views.order_details,name='order_details'),
    
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
