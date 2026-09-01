from django.contrib import admin

from .models import AttachedBody, Delegation, OrgUnit, Region, TrainingCenter


@admin.register(OrgUnit)
class OrgUnitAdmin(admin.ModelAdmin):
    list_display = ("name", "unit_type", "parent", "director_name", "order")
    list_filter = ("unit_type",)
    search_fields = ("name", "director_name")
    ordering = ("order",)
    autocomplete_fields = ("parent",)
    readonly_fields = ("slug",)


@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    list_display = ("name", "capital")


@admin.register(Delegation)
class DelegationAdmin(admin.ModelAdmin):
    list_display = ("__str__", "level", "region", "town", "delegate_name")
    list_filter = ("level", "region")


@admin.register(TrainingCenter)
class TrainingCenterAdmin(admin.ModelAdmin):
    list_display = ("name", "center_type", "region", "town", "is_public")
    list_filter = ("center_type", "region", "is_public")
    search_fields = ("name", "town")


@admin.register(AttachedBody)
class AttachedBodyAdmin(admin.ModelAdmin):
    list_display = ("name", "acronym", "kind", "order")
    list_filter = ("kind",)
    list_editable = ("order",)
