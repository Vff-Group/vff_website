from django.urls import path
from . import views

app_name = 'gym_mobile_app' #namespace

urlpatterns = [
     path('get_csrf_token/', views.get_csrf_token, name='get_csrf_token'),
    path('login/', views.login,name='login'),
    # path('register/', views.register_member,name='register'),
    path('complete_profile/', views.profile_complete,name='complete_profile'),
    path('set_goal/', views.set_goal,name='set_goal'),
    path('get_fees_details/', views.get_feesdetails,name='get_fees_details'),
    path('get_diet_chart_details/', views.get_diet_chart_details,name='get_diet_chart_details'),
    path('get_fees_chart_details/', views.get_fees_chart_details,name='get_fees_chart_details'),
    path('save_gym_fees/', views.save_gym_fees,name='save_gym_fees'),
    path('get_notification/', views.get_notification,name='get_notification'),
    #Update Notification Token
    path('update_notification_token/',views.update_notification_token,name='update_notification_token'),
    
    # path('aboutus/',views.about_us,name="aboutus"),
    # path('services/',views.services,name="services"),
    # path('contactus/',views.contactus,name="contactus"),
    # path('privacy_policy/',views.privacy,name="privacy"),

]