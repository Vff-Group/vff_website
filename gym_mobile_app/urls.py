from django.urls import path
from . import views

app_name = 'gym_mobile_app' #namespace

urlpatterns = [
    path('login/', views.login,name='login'),
    # path('aboutus/',views.about_us,name="aboutus"),
    # path('services/',views.services,name="services"),
    # path('contactus/',views.contactus,name="contactus"),
    # path('privacy_policy/',views.privacy,name="privacy"),

]