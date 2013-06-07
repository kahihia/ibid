from bidding.models import Auction
from django.contrib.sitemaps import Sitemap

class AuctionSitemap(Sitemap):
    changefreq = "never"
    priority = 0.5

    def items(self):
        return Auction.objects.filter(is_active=False)

    def lastmod(self, obj):
        return obj.won_date
