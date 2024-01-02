from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

app_name = 'gym_dashboard_app' #nameSpaceses

urlpatterns = [
    #Login
    path('',views.login_view,name='login'),
    
    #Gym branch Selection
    path('all_gym_branches/',views.all_gym_branches,name='all_gym_branches'),
    
    #Save Selected  GYM branch Details in a session
    path('selected_branches/',views.save_selected_gym_branch,name='selected_branches'),
   
    #Dashboard
    path('dashboard_gym/',views.dashboard_view,name='dashboard'),
   
    #All GYM Members
    path('all_gym_members/',views.all_gym_members,name='all_gym_members'),
   
    #Add New GYm Member
    path('add_new_gym_member/',views.add_new_gym_member,name='add_new_gym_member'),
   
    
    
    
    
    #All Fees Plans
    path('all_fees_plans/',views.all_fees_plans,name='all_fees_plans'),
   
    
   
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
