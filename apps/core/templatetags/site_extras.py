"""Small template helpers shared across the MINEFOP site."""

from django import template
from django.urls import translate_url

register = template.Library()


@register.simple_tag(takes_context=True)
def translated_url(context, language_code):
    """Return the absolute URL of the current page in ``language_code``.

    Used by the ``hreflang`` alternates in ``<head>``, which search engines only
    honour when the URLs are absolute, so that the French and English versions
    of every page are declared as translations of one another.
    """
    request = context.get("request")
    if request is None:
        return "/"
    return request.build_absolute_uri(translate_url(request.get_full_path(), language_code))
