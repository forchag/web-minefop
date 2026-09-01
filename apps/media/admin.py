from django.contrib import admin

from .models import Event, GalleryPhoto


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ("title", "start_at", "location", "is_published")
    list_filter = ("is_published",)
    search_fields = ("title", "description", "location")
    prepopulated_fields = {"slug": ("title",)}
    date_hierarchy = "start_at"


@admin.register(GalleryPhoto)
class GalleryPhotoAdmin(admin.ModelAdmin):
    list_display = ("title", "event", "order", "is_published", "uploaded_at")
    list_filter = ("is_published", "event")
    list_editable = ("order",)
