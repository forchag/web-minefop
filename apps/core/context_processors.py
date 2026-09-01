from django.conf import settings

# Groups of view names used by the primary navigation to decide which top-level
# menu should be marked as the active section.
MINISTRY_VIEWS = (
    "core:minister",
    "core:mission",
    "core:history",
    "structures:org_chart",
    "structures:directorate_list",
    "structures:directorate_detail",
    "structures:attached_bodies",
    "structures:delegations",
)

TRAINING_VIEWS = (
    "core:vocational_training",
)


def site_context(request):
    """Global template context available on every page."""
    from apps.contact.models import ContactInfo
    from apps.structures.models import OrgUnit

    return {
        "SITE_NAME": settings.SITE_NAME,
        "CONTACT_RECIPIENT_EMAIL": settings.CONTACT_RECIPIENT_EMAIL,
        "CURRENT_LANGUAGE_CODE": getattr(request, "LANGUAGE_CODE", "fr"),
        "site_contact_info": ContactInfo.load(),
        "ministry_views": MINISTRY_VIEWS,
        "training_views": TRAINING_VIEWS,
        "directorates_nav": OrgUnit.objects.filter(
            unit_type=OrgUnit.UnitType.DIRECTION, slug__isnull=False
        ).order_by("order"),
    }
