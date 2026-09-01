from django.utils import translation


class ForceFrenchDashboardMiddleware:
    """The dashboard's own chrome is not bilingual — only blog post *content*
    is (title_fr/title_en etc.). Dashboard URLs live outside i18n_patterns,
    so without this LocaleMiddleware would pick the UI language from the
    visiting browser's Accept-Language header, making the dashboard's
    French labels randomly show up in English. Pin it to French."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith("/dashboard/"):
            translation.activate("fr")
            request.LANGUAGE_CODE = "fr"
        return self.get_response(request)
