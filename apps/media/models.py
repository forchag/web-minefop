from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class Event(models.Model):
    """A ministry event: a launch ceremony, a signing, a job fair..."""

    title = models.CharField(_("titre"), max_length=250)
    slug = models.SlugField(_("slug"), max_length=270, unique=True)
    description = models.TextField(_("description"))
    location = models.CharField(_("lieu"), max_length=250, blank=True)
    start_at = models.DateTimeField(_("date et heure de début"), default=timezone.now)
    end_at = models.DateTimeField(_("date et heure de fin"), null=True, blank=True)
    cover_image = models.ImageField(_("image de couverture"), upload_to="events/", blank=True)
    is_published = models.BooleanField(_("publié"), default=True)

    class Meta:
        verbose_name = _("événement")
        verbose_name_plural = _("événements")
        ordering = ["-start_at"]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("media:event_detail", kwargs={"slug": self.slug})

    @property
    def is_upcoming(self):
        return self.start_at >= timezone.now()


class GalleryPhoto(models.Model):
    """A single photo in the ministry's public photo gallery, optionally
    tied to one Event."""

    title = models.CharField(_("légende"), max_length=200, blank=True)
    image = models.ImageField(_("photo"), upload_to="gallery/")
    event = models.ForeignKey(
        Event,
        verbose_name=_("événement"),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="photos",
    )
    is_published = models.BooleanField(_("publié"), default=True)
    order = models.PositiveIntegerField(_("ordre"), default=0)
    uploaded_at = models.DateTimeField(_("ajoutée le"), auto_now_add=True)

    class Meta:
        verbose_name = _("photo")
        verbose_name_plural = _("galerie photo")
        ordering = ["order", "-uploaded_at"]

    def __str__(self):
        return self.title or f"Photo #{self.pk}"
