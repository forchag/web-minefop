from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import Opportunity


@admin.register(Opportunity)
class OpportunityAdmin(admin.ModelAdmin):
    list_display = ("title", "kind", "organisme", "application_deadline", "is_published")
    list_filter = ("kind", "is_published")
    list_editable = ("is_published",)
    search_fields = ("title", "organisme", "summary", "description")
    prepopulated_fields = {"slug": ("title",)}
    date_hierarchy = "published_at"
    fieldsets = (
        (None, {"fields": ("title", "slug", "kind", "organisme")}),
        (_("Contenu"), {"fields": ("summary", "description", "conditions", "document")}),
        (
            _("Candidature"),
            {"fields": ("application_deadline", "application_url", "contact_email")},
        ),
        (_("Publication"), {"fields": ("is_published", "published_at")}),
    )
