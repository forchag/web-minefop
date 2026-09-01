from django.conf import settings
from django.utils import translation


class ForceFrenchDashboardMiddleware:
    """The dashboard's chrome defaults to French, but staff can switch it to
    English with the language switcher in the dashboard's own top bar (which
    sets the usual django_language cookie via the shared set_language view).
    Dashboard URLs live outside i18n_patterns, so without this,
    LocaleMiddleware would otherwise pick the UI language from the visiting
    browser's Accept-Language header alone, making the dashboard's labels
    randomly show up in English. Only an explicit choice — the cookie —
    overrides the French default; Accept-Language on its own is ignored."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith("/dashboard/") and settings.LANGUAGE_COOKIE_NAME not in request.COOKIES:
            translation.activate("fr")
            request.LANGUAGE_CODE = "fr"
        return self.get_response(request)
