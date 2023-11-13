# website_app/sitemaps.py
from django.contrib.sitemaps import Sitemap
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse

class StaticViewSitemap(Sitemap):
    priority = 0.5
    changefreq = 'daily'

    def items(self):
        return ['home', 'about', 'contact']  # Add your view names here

    def location(self, item):
        current_site = get_current_site(None)
        return f"{current_site.scheme}://{current_site.domain}{reverse(item)}"
