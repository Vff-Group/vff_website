from django.contrib.sitemaps import Sitemap
from website_app.models import Post
from django.urls import reverse

class PostSitemap(Sitemap):
    
    def items(self):
        return Post.objects.all()
    
    
    
class StaticViewSitemap(Sitemap):
    priority = 0.5
    changefreq = "weekly"
    def items(self):
        return ['website_app:index','website_app:aboutus','website_app:services','website_app:contactus','website_app:privacy']
    
    def location(self,item):
        return reverse(item)
    
    def get_absolute_path(self, item):
        return reverse(item)