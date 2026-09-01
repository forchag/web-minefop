from django.core.validators import FileExtensionValidator
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.core.validators import validate_file_size


class Opportunity(models.Model):
    """A job opening or a public-service recruitment exam ("concours")
    published by the Ministry or one of its attached bodies."""

    class Kind(models.TextChoices):
        JOB = "emploi", _("Offre d'emploi")
        CONCOURS = "concours", _("Concours")

    title = models.CharField(_("titre"), max_length=250)
    slug = models.SlugField(_("slug"), max_length=270, unique=True)
    kind = models.CharField(_("type"), max_length=10, choices=Kind.choices, default=Kind.JOB)
    organisme = models.CharField(
        _("organisme"),
        max_length=200,
        help_text=_("Structure qui recrute ou organise le concours (ex. MINEFOP, CNFFDP, une délégation régionale)."),
    )
    summary = models.CharField(_("résumé"), max_length=300)
    description = models.TextField(_("description"))
    conditions = models.TextField(
        _("conditions de candidature"),
        blank=True,
        help_text=_("Diplômes, âge, expérience ou autres critères d'éligibilité."),
    )
    application_deadline = models.DateField(
        _("date limite de candidature"),
        null=True,
        blank=True,
        help_text=_("Laisser vide si l'offre reste ouverte jusqu'à nouvel ordre."),
    )
    application_url = models.URLField(_("lien de candidature"), blank=True)
    contact_email = models.EmailField(_("courriel de contact"), blank=True)
    document = models.FileField(
        _("avis officiel (PDF)"),
        upload_to="opportunities/",
        blank=True,
        validators=[FileExtensionValidator(allowed_extensions=["pdf"]), validate_file_size],
        help_text=_("Avis de concours ou fiche de poste, au format PDF."),
    )
    published_at = models.DateTimeField(_("date de publication"), default=timezone.now)
    is_published = models.BooleanField(_("publié"), default=True)

    class Meta:
        verbose_name = _("opportunité")
        verbose_name_plural = _("opportunités & concours")
        ordering = ["-published_at"]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("opportunities:detail", kwargs={"slug": self.slug})

    @property
    def is_open(self):
        if not self.application_deadline:
            return True
        return self.application_deadline >= timezone.localdate()
