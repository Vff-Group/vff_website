"""
URL configuration for vff_website_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include
from dashboard_app.views import *
from website_app.sitemaps import PostSitemap,StaticViewSitemap
from django.contrib.sitemaps.views import sitemap
from website_app.views import custom_404_view,custom_500_view
from united_armor_website.views import custom_404_view_united,custom_500_view_united

sitemaps = {
    'static':StaticViewSitemap,
}


urlpatterns = [
    path('admin/', admin.site.urls),
    path('',include('website_app.urls',namespace='website_app')),
    # path('send/' , send),
    # path('firebase-messaging-sw.js',showFirebaseJS,name="show_firebase_js"),
    path('admin_dashboard/',include('dashboard_app.urls',namespace='dashboard_app')),
    path('gym_mobile_app/',include('gym_mobile_app.urls',namespace='gym_mobile_app')),
    path('clothing_mobile_app/',include('clothing_mobile_app.urls',namespace='clothing_mobile_app')),
    path('laundry_mobile_app/',include('laundry_mobile_app.urls',namespace='laundry_mobile_app')),
    path('clothing_dashboard_app/',include('clothing_dashboard.urls',namespace='clothing_dashboard_app')),
    path('gym_dashboard_app/',include('gym_dashboard.urls',namespace='gym_dashboard_app')),
    path('united_armor/',include('united_armor_website.urls',namespace='united_armor')),
    path("django-check-seo/", include("django_check_seo.urls")),
    path('sitemaps.xml',sitemap ,{'sitemaps':sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
    
]

# For united_armor app
handler404 = custom_404_view_united
handler500 = custom_500_view_united

# handler404 = custom_404_view
# handler500 = custom_500_view
