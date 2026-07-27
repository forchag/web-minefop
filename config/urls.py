"""
URL configuration for the MINEFOP website.
"""

from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

# URLs that must NOT be language-prefixed (admin, language switcher).
urlpatterns = [
    path("admin/", admin.site.urls),
    path("i18n/", include("django.conf.urls.i18n")),
]

# All public-facing pages are served under a /fr/ or /en/ prefix.
urlpatterns += i18n_patterns(
    path("", include("apps.core.urls")),
    path("actualites/", include("apps.news.urls")),
    path("documents/", include("apps.documents.urls")),
    path("organisation/", include("apps.structures.urls")),
    path("contact/", include("apps.contact.urls")),
    prefix_default_language=True,
)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])

handler404 = "apps.core.views.error_404"
handler500 = "apps.core.views.error_500"
