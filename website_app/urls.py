from django.urls import path
from . import views
urlpatterns = [
    path('', views.index,name='index'),
    path('aboutus/',views.about_us,name="aboutus"),
    path('services/',views.services,name="services"),
    path('contactus/',views.contactus,name="contactus"),
]
