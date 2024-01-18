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
   
    #AddNew Gym Member
    path('add_new_gym_member/',views.add_new_gym_member,name='add_new_gym_member'),
   
    #Update  Gym Member Details
    path('update_gym_member/<int:member_id>/',views.update_gym_member,name='update_gym_member'),
   
    #All Fees Plans
    path('all_fees_plans/',views.all_fees_plans,name='all_fees_plans'),
    
    #AddNew Fees Plan
    path('add_new_fees_plan/',views.add_new_fees_plan,name='add_new_fees_plan'),
   
    #Update  Fees Plan
    path('update_fees_plan/<int:fees_plan_id>/',views.update_fees_plan,name='update_fees_plan'),
   
    #All Due Fees Members Details
    path('fees_due_details/',views.fees_due_details,name='fees_due_details'),
   
    #All Fees Plans
    path('fetch_fees_plans/',views.fetch_fees_plans,name='fetch_fees_plans'),
   
    #Due Fees Paid Update
    path('update_fees_paid_details/',views.update_fees_payment_details_for_member,name='update_fees_paid_details'),
   
    #All New Admissions
    path('all_new_admissions_members_details/',views.all_new_admissions_members_details,name='all_new_admissions_members_details'),
   
    #All New Admissions
    path('make_admission_payment/<int:member_id>/<str:name>/<str:due_date>/',views.make_admission_payment,name='make_admission_payment'),
   
    #New Admission Fees Details Add and Update
    path('add_new_admission_fees_details/',views.add_new_admission_fees_details,name='add_new_admission_fees_details'),
   
   
    
   
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
