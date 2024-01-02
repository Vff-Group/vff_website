from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

app_name = 'gym_dashboard_app' #nameSpaceses

urlpatterns = [
    #Login
    path('',views.login_view,name='login'),
    
    #Gym branch Selection
    path('select_branch/',views.select_branch,name='select_branch'),
   
    #Dashboard
    path('dashboard_gym/',views.dashboard_view,name='dashboard'),
   
    #All Customers
    path('all_gym_members/',views.all_gym_members,name='all_gym_members'),
   
    
   
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
