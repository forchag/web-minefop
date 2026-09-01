from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.forms import inlineformset_factory
from django.utils.translation import gettext_lazy as _

from apps.blog.models import MAX_ATTACHMENTS_PER_POST, BlogAttachment, BlogPost
from apps.news.models import Article


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
