from django.urls import path
from . import views

app_name = 'gym_mobile_app' #namespace

urlpatterns = [
     path('get_csrf_token/', views.get_csrf_token, name='get_csrf_token'),
    path('login/', views.login,name='login'),
    # path('register/', views.register_member,name='register'),
    path('complete_profile/', views.profile_complete,name='complete_profile'),
    
    # path('aboutus/',views.about_us,name="aboutus"),
    # path('services/',views.services,name="services"),
    # path('contactus/',views.contactus,name="contactus"),
    # path('privacy_policy/',views.privacy,name="privacy"),

]