from django.conf import settings


def site_context(request):
    """Global template context available on every page."""
    return {
        "SITE_NAME": settings.SITE_NAME,
        "CONTACT_RECIPIENT_EMAIL": settings.CONTACT_RECIPIENT_EMAIL,
        "CURRENT_LANGUAGE_CODE": getattr(request, "LANGUAGE_CODE", "fr"),
    }
