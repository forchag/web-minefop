from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from .models import MAX_ATTACHMENTS_PER_POST, BlogAttachment, BlogPost


class BlogAttachmentInline(admin.TabularInline):
    model = BlogAttachment
    extra = 1
    max_num = MAX_ATTACHMENTS_PER_POST
    fields = ("file", "title", "order", "file_preview")
    readonly_fields = ("file_preview",)

    def get_formset(self, request, obj=None, **kwargs):
        # max_num alone only limits how many empty rows the admin renders and
        # disables the "add another" link client-side once reached; without
        # validate_max a forged POST could still slip more past it. This makes
        # the cap a real server-side rule.
        kwargs["validate_max"] = True
        return super().get_formset(request, obj, **kwargs)

    @admin.display(description=_("aperçu"))
    def file_preview(self, obj):
        if not obj.pk or not obj.file:
            return "—"
        if obj.extension in {"jpg", "jpeg", "png", "webp"}:
            return format_html(
                '<img src="{}" style="height:40px;width:auto;border-radius:2px;">', obj.file.url
            )
        return format_html(
            '<a href="{}" target="_blank" rel="noopener">{}</a>', obj.file.url, obj.extension.upper()
        )


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = (
        "cover_thumbnail",
        "title",
        "author_name",
        "published_at",
        "is_published",
        "attachment_count",
    )
    list_display_links = ("title",)
    list_filter = ("is_published",)
    list_editable = ("is_published",)
    search_fields = ("title", "author_name", "excerpt", "body")
    prepopulated_fields = {"slug": ("title",)}
    date_hierarchy = "published_at"
    inlines = [BlogAttachmentInline]
    readonly_fields = ("created_by", "created_at", "updated_at")
    fieldsets = (
        (None, {"fields": ("title", "slug", "author_name")}),
        (_("Contenu"), {"fields": ("excerpt", "body", "cover_image")}),
        (_("Publication"), {"fields": ("is_published", "published_at")}),
        (
            _("Traçabilité"),
            {"classes": ("collapse",), "fields": ("created_by", "created_at", "updated_at")},
        ),
    )

    @admin.display(description=_("couverture"))
    def cover_thumbnail(self, obj):
        if not obj.cover_image:
            return "—"
        return format_html(
            '<img src="{}" style="height:36px;width:56px;object-fit:cover;border-radius:3px;">',
            obj.cover_image.url,
        )

    @admin.display(description=_("documents"))
    def attachment_count(self, obj):
        return f"{obj.attachments.count()}/{MAX_ATTACHMENTS_PER_POST}"

    def get_changeform_initial_data(self, request):
        initial = super().get_changeform_initial_data(request)
        # A convenience default, not a constraint: the byline stays a plain
        # text field so a post can be published under a Minister's name, a
        # service, or a communications cell rather than only a login name.
        initial.setdefault("author_name", request.user.get_full_name() or request.user.get_username())
        return initial

    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
