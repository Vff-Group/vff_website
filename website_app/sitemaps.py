from django.contrib.sitemaps import Sitemap
from website_app.models import Post

class PostSitemap(Sitemap):
    
    def items(self):
        return Post.objects.all()