from django.db import models
from django.utils.translation import gettext_lazy as _


class DocumentCategory(models.Model):
    name = models.CharField(_("nom"), max_length=100)
    slug = models.SlugField(_("slug"), max_length=110, unique=True)
    order = models.PositiveIntegerField(_("ordre"), default=0)

    class Meta:
        verbose_name = _("catégorie de document")
        verbose_name_plural = _("catégories de documents")
        ordering = ["order", "name"]

    def __str__(self):
        return self.name


class Document(models.Model):
    title = models.CharField(_("titre"), max_length=300)
    category = models.ForeignKey(
        DocumentCategory,
        verbose_name=_("catégorie"),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="documents",
    )
    reference_number = models.CharField(
        _("référence"),
        max_length=150,
        blank=True,
        help_text=_("Ex : Loi n° 2018/010 du 11 juillet 2018"),
    )
    description = models.TextField(_("description"), blank=True)
    file = models.FileField(_("fichier PDF"), upload_to="documents/", blank=True)
    source_url = models.URLField(
        _("adresse du fichier"),
        max_length=500,
        blank=True,
        help_text=_(
            "À utiliser lorsque le document n'a pas encore été téléversé et reste "
            "hébergé à son adresse d'origine. Le fichier téléversé prévaut."
        ),
    )
    published_date = models.DateField(_("date de signature/publication"), null=True, blank=True)

    class Meta:
        verbose_name = _("document")
        verbose_name_plural = _("documents")
        ordering = ["-published_date", "title"]

    def __str__(self):
        return self.title

    @property
    def download_url(self):
        """Where the public can actually fetch the document."""
        if self.file:
            return self.file.url
        return self.source_url
