"""Sitemaps published at /sitemap.xml so search engines can index the site."""

from django.contrib.sitemaps import Sitemap
from django.urls import reverse


class StaticViewSitemap(Sitemap):
    """The institutional pages, which change rarely but matter most."""

    changefreq = "monthly"
    protocol = "https"

    def items(self):
        return [
            ("core:home", 1.0),
            ("core:mission", 0.8),
            ("core:minister", 0.8),
            ("core:history", 0.6),
            ("core:vocational_training", 0.8),
            ("structures:org_chart", 0.7),
            ("structures:attached_bodies", 0.6),
            ("structures:delegations", 0.7),
            ("structures:training_center_list", 0.9),
            ("documents:list", 0.9),
            ("news:list", 0.9),
            ("contact:contact", 0.7),
            ("core:legal_notice", 0.3),
            ("core:accessibility", 0.3),
            ("core:sitemap_page", 0.3),
        ]

    def location(self, item):
        return reverse(item[0])

    def priority(self, item):
        return item[1]


class ArticleSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.7
    protocol = "https"

    def items(self):
        from apps.news.models import Article

        return Article.objects.filter(is_published=True)

    def lastmod(self, obj):
        return obj.published_at


class TrainingCenterSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.6
    protocol = "https"

    def items(self):
        from apps.structures.models import TrainingCenter

        return TrainingCenter.objects.all()


SITEMAPS = {
    "pages": StaticViewSitemap,
    "actualites": ArticleSitemap,
    "centres": TrainingCenterSitemap,
}
