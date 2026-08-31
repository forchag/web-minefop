import os

from django.conf import settings
from django.core.validators import FileExtensionValidator
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from .validators import validate_file_size

#: Kept narrow on purpose: supporting material for a post (reports, decisions,
#: forms, photos of an event) rather than an open upload of any file type.
ATTACHMENT_EXTENSIONS = [
    "pdf",
    "doc",
    "docx",
    "xls",
    "xlsx",
    "ppt",
    "pptx",
    "jpg",
    "jpeg",
    "png",
    "webp",
]

#: How many supporting documents a single post may carry. Enforced in
#: BlogAttachmentInline (apps/blog/admin.py) via validate_max=True — the admin
#: is the only interface that creates these, so that is where the limit has to
#: live to actually be checked server-side rather than just in the browser.
MAX_ATTACHMENTS_PER_POST = 10


class BlogPost(models.Model):
    """An editorial post: the Ministry's own voice, distinct from the
    Actualités communiqués (apps.news) and shown with a named author."""

    title = models.CharField(_("titre"), max_length=250)
    slug = models.SlugField(_("slug"), max_length=270, unique=True)
    author_name = models.CharField(
        _("auteur"),
        max_length=150,
        help_text=_(
            "Nom affiché publiquement comme auteur de l'article "
            "(personne, service ou cellule de communication)."
        ),
    )
    excerpt = models.CharField(
        _("chapô"),
        max_length=300,
        help_text=_("Court résumé affiché dans la liste des articles."),
    )
    body = models.TextField(_("contenu"))
    cover_image = models.ImageField(
        _("image de couverture"),
        upload_to="blog/covers/",
        validators=[validate_file_size],
        help_text=_("Image mise en avant en tête d'article et dans la liste du blog."),
    )
    published_at = models.DateTimeField(_("date de publication"), default=timezone.now)
    is_published = models.BooleanField(_("publié"), default=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_("créé par"),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        editable=False,
        related_name="blog_posts",
        help_text=_(
            "Compte de l'espace d'administration ayant créé l'article — "
            "distinct du nom d'auteur affiché publiquement."
        ),
    )
    created_at = models.DateTimeField(_("créé le"), auto_now_add=True)
    updated_at = models.DateTimeField(_("modifié le"), auto_now=True)

    class Meta:
        verbose_name = _("article de blog")
        verbose_name_plural = _("articles de blog")
        ordering = ["-published_at"]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("blog:detail", kwargs={"slug": self.slug})


class BlogAttachment(models.Model):
    """A supporting document attached to a blog post (up to 10 per post)."""

    post = models.ForeignKey(
        BlogPost, verbose_name=_("article"), on_delete=models.CASCADE, related_name="attachments"
    )
    file = models.FileField(
        _("document"),
        upload_to="blog/attachments/",
        validators=[
            FileExtensionValidator(allowed_extensions=ATTACHMENT_EXTENSIONS),
            validate_file_size,
        ],
    )
    title = models.CharField(
        _("titre du document"),
        max_length=200,
        blank=True,
        help_text=_("Affiché à la place du nom de fichier ; laisser vide pour l'utiliser tel quel."),
    )
    order = models.PositiveIntegerField(_("ordre"), default=0)

    class Meta:
        verbose_name = _("document joint")
        verbose_name_plural = _("documents joints")
        ordering = ["order", "id"]

    def __str__(self):
        return self.display_title

    @property
    def display_title(self):
        return self.title or os.path.basename(self.file.name)

    @property
    def extension(self):
        return os.path.splitext(self.file.name)[1].lstrip(".").lower()
