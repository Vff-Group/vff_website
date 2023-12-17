from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

app_name = 'clothing_dashboard_app' #nameSpaceses

urlpatterns = [
    #Login
    path('',views.login_view,name='login'),
    path('dashboard/',views.dashboard_view,name='dashboard'),
   
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
