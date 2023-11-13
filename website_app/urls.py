from django.urls import path
from . import views
from .sitemaps import StaticViewSitemap
from django.contrib.sitemaps.views import sitemap

sitemaps = {
    'static': StaticViewSitemap,
}
app_name = 'website_app' #namespace

urlpatterns = [
    path('', views.index,name='index'),
    path('aboutus/',views.about_us,name="aboutus"),
    path('services/',views.services,name="services"),
    path('contactus/',views.contactus,name="contactus"),
    path('privacy_policy/',views.privacy,name="privacy"),
     path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
]
