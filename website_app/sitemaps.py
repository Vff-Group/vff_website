from django.contrib.sitemaps import Sitemap
from website_app.models import Post
from django.urls import reverse

class PostSitemap(Sitemap):
    
    def items(self):
        return Post.objects.all()
    
class StaticViewSitemap(Sitemap):
    
    def items(self):
        return ['index','aboutus','services','contactus','privacy']
    
    def location(self,item):
        return reverse(item)