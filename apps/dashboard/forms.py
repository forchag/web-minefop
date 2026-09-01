from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.forms import inlineformset_factory
from django.utils.translation import gettext_lazy as _

from apps.blog.models import MAX_ATTACHMENTS_PER_POST, BlogAttachment, BlogPost
from apps.documents.models import Document
from apps.media.models import Event, GalleryPhoto
from apps.news.models import Article
from apps.opportunities.models import Opportunity
from apps.structures.models import OrgUnit


class BootstrapFormMixin:
    """Applies the site's Bootstrap form styling to every field so templates
    can just do `{{ field }}` without repeating widget attrs everywhere."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            widget = field.widget
            if isinstance(widget, forms.CheckboxInput):
                widget.attrs.setdefault("class", "form-check-input")
            elif isinstance(widget, (forms.Select, forms.SelectMultiple)):
                widget.attrs.setdefault("class", "form-select")
            else:
                widget.attrs.setdefault("class", "form-control")


class DashboardLoginForm(BootstrapFormMixin, AuthenticationForm):
    error_messages = {
        **AuthenticationForm.error_messages,
        "invalid_login": _(
            "Identifiant ou mot de passe incorrect, ou compte non autorisé à accéder au tableau de bord."
        ),
    }

    def confirm_login_allowed(self, user):
        super().confirm_login_allowed(user)
        if not user.is_staff:
            raise forms.ValidationError(
                self.error_messages["invalid_login"],
                code="invalid_login",
            )


class BlogPostForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = BlogPost
        fields = [
            "title_fr",
            "title_en",
            "author_name",
            "excerpt_fr",
            "excerpt_en",
            "body_fr",
            "body_en",
            "cover_image",
            "is_published",
            "published_at",
        ]
        widgets = {
            "excerpt_fr": forms.Textarea(attrs={"rows": 2}),
            "excerpt_en": forms.Textarea(attrs={"rows": 2}),
            "body_fr": forms.Textarea(attrs={"rows": 10}),
            "body_en": forms.Textarea(attrs={"rows": 10}),
            "published_at": forms.DateTimeInput(attrs={"type": "datetime-local"}, format="%Y-%m-%dT%H:%M"),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["published_at"].input_formats = ["%Y-%m-%dT%H:%M"]


BlogAttachmentFormSet = inlineformset_factory(
    BlogPost,
    BlogAttachment,
    fields=["file", "title", "order"],
    extra=1,
    max_num=MAX_ATTACHMENTS_PER_POST,
    validate_max=True,
    can_delete=True,
)


class ArticleForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Article
        fields = [
            "title",
            "category",
            "excerpt",
            "body",
            "cover_image",
            "is_published",
            "published_at",
        ]
        widgets = {
            "excerpt": forms.Textarea(attrs={"rows": 2}),
            "body": forms.Textarea(attrs={"rows": 10}),
            "published_at": forms.DateTimeInput(attrs={"type": "datetime-local"}, format="%Y-%m-%dT%H:%M"),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["published_at"].input_formats = ["%Y-%m-%dT%H:%M"]


class OpportunityForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Opportunity
        fields = [
            "title",
            "kind",
            "organisme",
            "summary",
            "description",
            "conditions",
            "application_deadline",
            "application_url",
            "contact_email",
            "document",
            "is_published",
            "published_at",
        ]
        widgets = {
            "summary": forms.Textarea(attrs={"rows": 2}),
            "description": forms.Textarea(attrs={"rows": 8}),
            "conditions": forms.Textarea(attrs={"rows": 4}),
            "application_deadline": forms.DateInput(attrs={"type": "date"}),
            "published_at": forms.DateTimeInput(attrs={"type": "datetime-local"}, format="%Y-%m-%dT%H:%M"),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["published_at"].input_formats = ["%Y-%m-%dT%H:%M"]


class DocumentForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Document
        fields = [
            "title",
            "category",
            "reference_number",
            "description",
            "file",
            "source_url",
            "published_date",
        ]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
            "published_date": forms.DateInput(attrs={"type": "date"}),
        }


class EventForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Event
        fields = [
            "title",
            "description",
            "location",
            "start_at",
            "end_at",
            "cover_image",
            "is_published",
        ]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 6}),
            "start_at": forms.DateTimeInput(attrs={"type": "datetime-local"}, format="%Y-%m-%dT%H:%M"),
            "end_at": forms.DateTimeInput(attrs={"type": "datetime-local"}, format="%Y-%m-%dT%H:%M"),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["start_at"].input_formats = ["%Y-%m-%dT%H:%M"]
        self.fields["end_at"].input_formats = ["%Y-%m-%dT%H:%M"]


class GalleryPhotoForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = GalleryPhoto
        fields = ["title", "image", "event", "order", "is_published"]


class DirectorateForm(BootstrapFormMixin, forms.ModelForm):
    """Scoped on purpose: for the directorates and sub-directorates that
    come from the decree (name, hierarchy, legal reference fixed by law),
    only the page-content fields an editor should be updating day to day
    (mission text and who to contact) are exposed here."""

    class Meta:
        model = OrgUnit
        fields = ["mission", "director_name", "director_email"]
        widgets = {
            "mission": forms.Textarea(attrs={"rows": 6}),
        }


class OrgUnitCreateForm(BootstrapFormMixin, forms.ModelForm):
    """Used to add a directorate or sub-directorate that isn't part of the
    original decree-derived org chart (e.g. one created by a later
    reorganisation). Unlike DirectorateForm, the name and hierarchy fields
    are open here since there is no decree text to keep them in sync with —
    the view sets unit_type and parent itself."""

    class Meta:
        model = OrgUnit
        fields = ["name", "head_title", "legal_reference", "mission", "director_name", "director_email", "order"]
        widgets = {
            "mission": forms.Textarea(attrs={"rows": 6}),
        }
