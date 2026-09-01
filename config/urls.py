"""
URL configuration for the MINEFOP website.
"""

from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.urls import include, path

from apps.core.sitemaps import SITEMAPS
from apps.core.views import portal, robots_txt

# URLs that must NOT be language-prefixed: the bilingual entry portal (which is
# the door to both language versions), the admin, the language switcher and the
# crawler files.
urlpatterns = [
    path("", portal, name="portal"),
    path("admin/", admin.site.urls),
    path("dashboard/", include("apps.dashboard.urls")),
    path("i18n/", include("django.conf.urls.i18n")),
    path("robots.txt", robots_txt, name="robots_txt"),
    path(
        "sitemap.xml",
        sitemap,
        {"sitemaps": SITEMAPS},
        name="django.contrib.sitemaps.views.sitemap",
    ),
]

# All public-facing pages are served under a /fr/ or /en/ prefix.
urlpatterns += i18n_patterns(
    path("", include("apps.core.urls")),
    path("actualites/", include("apps.news.urls")),
    path("blog/", include("apps.blog.urls")),
    path("presse/", include("apps.press.urls")),
    path("opportunites/", include("apps.opportunities.urls")),
    path("documents/", include("apps.documents.urls")),
    path("", include("apps.media.urls")),
    path("organisation/", include("apps.structures.urls")),
    path("contact/", include("apps.contact.urls")),
    prefix_default_language=True,
)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])

handler404 = "apps.core.views.error_404"
handler500 = "apps.core.views.error_500"
