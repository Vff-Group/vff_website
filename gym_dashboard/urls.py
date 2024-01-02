from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

app_name = 'gym_dashboard_app' #nameSpaceses

urlpatterns = [
    #Login
    path('',views.login_view,name='login'),
   
    #Dashboard
    path('dashboard_gym/',views.dashboard_view,name='dashboard'),
   
    #All Customers
    path('all_customers_gym/',views.all_customers,name='all_customers'),
   
    
   
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
