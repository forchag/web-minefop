from django.db import models
from django.utils.translation import gettext_lazy as _


class HeroSlide(models.Model):
    """A slide in the homepage carousel."""

    title = models.CharField(_("titre"), max_length=200)
    subtitle = models.CharField(_("sous-titre"), max_length=300, blank=True)
    image = models.ImageField(_("image"), upload_to="hero/", blank=True, null=True)
    link_label = models.CharField(_("libellé du lien"), max_length=100, blank=True)
    link_url = models.CharField(_("URL du lien"), max_length=300, blank=True)
    order = models.PositiveIntegerField(_("ordre"), default=0)
    is_active = models.BooleanField(_("actif"), default=True)

    class Meta:
        verbose_name = _("diapositive d'accueil")
        verbose_name_plural = _("diapositives d'accueil")
        ordering = ["order", "id"]

    def __str__(self):
        return self.title


class KeyFigure(models.Model):
    """A statistic highlighted on the homepage (e.g. number of training centres)."""

    label = models.CharField(_("libellé"), max_length=150)
    value = models.CharField(_("valeur"), max_length=50)
    icon = models.CharField(
        _("icône (bootstrap-icons)"), max_length=50, default="bi-bar-chart-fill"
    )
    order = models.PositiveIntegerField(_("ordre"), default=0)

    class Meta:
        verbose_name = _("chiffre clé")
        verbose_name_plural = _("chiffres clés")
        ordering = ["order", "id"]

    def __str__(self):
        return f"{self.value} — {self.label}"


class MinisterMessage(models.Model):
    """Singleton-style model holding the Minister's welcome message."""

    full_name = models.CharField(
        _("nom complet"),
        max_length=200,
        blank=True,
        help_text=_(
            "À renseigner par le Ministère avec le nom officiel du Ministre en exercice."
        ),
    )
    title = models.CharField(
        _("titre / fonction"),
        max_length=200,
        default=_("Ministre de l'Emploi et de la Formation Professionnelle"),
    )
    photo = models.ImageField(_("photo"), upload_to="cabinet/", blank=True, null=True)
    message = models.TextField(_("mot du ministre"))
    updated_at = models.DateTimeField(_("dernière mise à jour"), auto_now=True)

    class Meta:
        verbose_name = _("mot du ministre")
        verbose_name_plural = _("mot du ministre")

    def __str__(self):
        return str(self.title)

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, _created = cls.objects.get_or_create(pk=1)
        return obj


class Timeline(models.Model):
    """A milestone in the institutional history of the ministry."""

    year = models.CharField(_("année"), max_length=10)
    title = models.CharField(_("titre"), max_length=250)
    description = models.TextField(_("description"), blank=True)
    order = models.PositiveIntegerField(_("ordre"), default=0)

    class Meta:
        verbose_name = _("étape historique")
        verbose_name_plural = _("historique")
        ordering = ["order", "year"]

    def __str__(self):
        return f"{self.year} — {self.title}"
