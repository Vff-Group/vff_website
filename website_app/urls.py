from django.urls import path
from . import views

app_name = 'website_app' #namespace

urlpatterns = [
    path('', views.index,name='index'),
    path('aboutus/',views.about_us,name="aboutus"),
    path('services/',views.services,name="services"),
    path('franchise/',views.franchise,name="franchise"),
    path('contactus/',views.contactus,name="contactus"),
    path('privacy_policy/',views.privacy,name="privacy"),
    path('terms_of_service/',views.terms_of_service,name="terms_of_service"),
    path('contact_form_submit/',views.contact_form_submit,name="contact_form_submit"),
    #  path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
]
