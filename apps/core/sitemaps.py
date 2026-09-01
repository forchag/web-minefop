"""Sitemaps published at /sitemap.xml so search engines can index the site."""

from itertools import chain

from django.contrib.sitemaps import Sitemap
from django.urls import reverse


class StaticViewSitemap(Sitemap):
    """The institutional pages, which change rarely but matter most."""

    changefreq = "monthly"
    protocol = "https"

    def items(self):
        return [
            # The bilingual entry portal at the root of the domain.
            ("portal", 1.0),
            ("core:home", 0.9),
            ("core:mission", 0.8),
            ("core:minister", 0.8),
            ("core:history", 0.6),
            ("structures:directorate_list", 0.6),
            ("core:vocational_training", 0.8),
            ("structures:org_chart", 0.7),
            ("structures:attached_bodies", 0.6),
            ("structures:delegations", 0.7),
            ("structures:training_center_list", 0.9),
            ("documents:list", 0.9),
            ("media:event_list", 0.7),
            ("media:gallery_list", 0.6),
            ("press:list", 0.9),
            ("opportunities:list", 0.8),
            ("contact:contact", 0.7),
            ("core:legal_notice", 0.3),
            ("core:accessibility", 0.3),
            ("core:sitemap_page", 0.3),
        ]

    def location(self, item):
        return reverse(item[0])

    def priority(self, item):
        return item[1]


class DirectorateSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.5
    protocol = "https"

    def items(self):
        from apps.structures.models import OrgUnit

        return OrgUnit.objects.filter(unit_type=OrgUnit.UnitType.DIRECTION, slug__isnull=False)


class PressSitemap(Sitemap):
    """The merged "Communiqués de presse" section: news articles and blog
    posts share one URL space (apps.press), so they share one sitemap."""

    changefreq = "weekly"
    priority = 0.7
    protocol = "https"

    def items(self):
        from apps.blog.models import BlogPost
        from apps.news.models import Article

        articles = list(Article.objects.filter(is_published=True))
        posts = list(BlogPost.objects.filter(is_published=True))
        return list(chain(articles, posts))

    def lastmod(self, obj):
        return getattr(obj, "updated_at", None) or obj.published_at


class OpportunitySitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.6
    protocol = "https"

    def items(self):
        from apps.opportunities.models import Opportunity

        return Opportunity.objects.filter(is_published=True)

    def lastmod(self, obj):
        return obj.published_at


class EventSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.5
    protocol = "https"

    def items(self):
        from apps.media.models import Event

        return Event.objects.filter(is_published=True)


class TrainingCenterSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.6
    protocol = "https"

    def items(self):
        from apps.structures.models import TrainingCenter

        return TrainingCenter.objects.all()


SITEMAPS = {
    "pages": StaticViewSitemap,
    "directions": DirectorateSitemap,
    "presse": PressSitemap,
    "opportunites": OpportunitySitemap,
    "evenements": EventSitemap,
    "centres": TrainingCenterSitemap,
}
