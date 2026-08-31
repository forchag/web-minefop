from django.contrib import admin

from .models import HeroSlide, KeyFigure, MinisterMessage, PartnerSite, Timeline


@admin.register(HeroSlide)
class HeroSlideAdmin(admin.ModelAdmin):
    list_display = ("title", "order", "is_active")
    list_editable = ("order", "is_active")
    ordering = ("order",)


@admin.register(KeyFigure)
class KeyFigureAdmin(admin.ModelAdmin):
    list_display = ("label", "value", "icon", "order")
    list_editable = ("order",)
    ordering = ("order",)


@admin.register(MinisterMessage)
class MinisterMessageAdmin(admin.ModelAdmin):
    list_display = ("title", "full_name", "updated_at")

    def has_add_permission(self, request):
        # Singleton: only one Minister's message record.
        return not MinisterMessage.objects.exists()


@admin.register(Timeline)
class TimelineAdmin(admin.ModelAdmin):
    list_display = ("year", "title", "order")
    list_editable = ("order",)
    ordering = ("order",)


@admin.register(PartnerSite)
class PartnerSiteAdmin(admin.ModelAdmin):
    list_display = ("name", "acronym", "column", "order", "tint", "has_local_logo", "is_active")
    list_filter = ("column", "group", "is_active")
    list_editable = ("column", "order", "is_active")
    search_fields = ("name", "acronym")
    ordering = ("column", "order")

    @admin.display(boolean=True, description="logo hébergé ici")
    def has_local_logo(self, obj):
        """False means the tile still loads its logo from the supplied address."""
        return bool(obj.logo)
