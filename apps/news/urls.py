from django.urls import path
from django.views.generic import RedirectView

app_name = "news"

# News articles are now shown through the merged "Communiqués de presse"
# section (apps.press) — these routes stay only as permanent redirects for
# anyone with an old /actualites/ link bookmarked or indexed.
urlpatterns = [
    path("", RedirectView.as_view(pattern_name="press:list", permanent=True), name="list"),
    path(
        "<slug:slug>/",
        RedirectView.as_view(pattern_name="press:detail", permanent=True),
        name="detail",
    ),
]
