from django.db import models
from django.utils.translation import gettext_lazy as _


class ContactInfo(models.Model):
    """Singleton holding the ministry's public contact details."""

    address = models.CharField(
        _("adresse"), max_length=300, default=_("Avenue Winston Churchill, Yaoundé, Cameroun")
    )
    po_box = models.CharField(_("boîte postale"), max_length=50, blank=True)
    phone = models.CharField(_("téléphone"), max_length=50, blank=True)
    email = models.EmailField(_("courriel"), default="contact@minefop.gov.cm")
    opening_hours = models.CharField(
        _("horaires d'ouverture"),
        max_length=200,
        default=_("Lundi – Vendredi : 7h30 – 15h30"),
    )
    map_embed_url = models.URLField(_("URL de la carte (iframe)"), blank=True)
    facebook_url = models.URLField(_("Facebook"), blank=True)
    twitter_url = models.URLField(_("X (Twitter)"), blank=True)
    linkedin_url = models.URLField(_("LinkedIn"), blank=True)
    youtube_url = models.URLField(_("YouTube"), blank=True)

    class Meta:
        verbose_name = _("informations de contact")
        verbose_name_plural = _("informations de contact")

    def __str__(self):
        return str(_("Informations de contact"))

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, _created = cls.objects.get_or_create(pk=1)
        return obj


class ContactMessage(models.Model):
    name = models.CharField(_("nom complet"), max_length=150)
    email = models.EmailField(_("courriel"))
    phone = models.CharField(_("téléphone"), max_length=50, blank=True)
    subject = models.CharField(_("objet"), max_length=200)
    message = models.TextField(_("message"))
    created_at = models.DateTimeField(_("date d'envoi"), auto_now_add=True)
    is_read = models.BooleanField(_("lu"), default=False)

    class Meta:
        verbose_name = _("message de contact")
        verbose_name_plural = _("messages de contact")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.subject} — {self.name}"
