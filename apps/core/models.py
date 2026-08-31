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


class PartnerSite(models.Model):
    """An institutional website listed on the public entry portal.

    The portal page that greets visitors at the root of the domain lists the
    institutions of the Republic, the bodies and projects working alongside the
    Ministry, and the online services citizens can reach directly.
    """

    class Group(models.TextChoices):
        INSTITUTION = "institution", _("Institutions de la République")
        PARTNER = "partner", _("Organismes, projets et partenaires")
        SERVICE = "service", _("Services et plateformes en ligne")

    name = models.CharField(_("nom"), max_length=250)
    acronym = models.CharField(
        _("sigle"),
        max_length=30,
        blank=True,
        help_text=_("Affiché en vignette lorsque aucun logo n'est téléversé."),
    )
    group = models.CharField(
        _("rubrique"), max_length=20, choices=Group.choices, default=Group.PARTNER
    )
    url = models.URLField(
        _("adresse du site"),
        max_length=300,
        blank=True,
        help_text=_("Laisser vide pour une structure dont le site n'est pas encore publié."),
    )
    description = models.CharField(_("description"), max_length=250, blank=True)
    logo = models.ImageField(_("logo"), upload_to="partners/", blank=True, null=True)
    order = models.PositiveIntegerField(_("ordre"), default=0)
    is_active = models.BooleanField(_("affiché sur le portail"), default=True)

    class Meta:
        verbose_name = _("site partenaire")
        verbose_name_plural = _("sites partenaires")
        ordering = ["group", "order", "name"]

    def __str__(self):
        return f"{self.acronym} — {self.name}" if self.acronym else self.name

    #: Icon standing in for a partner that has no logo uploaded yet. Letters
    #: would clip or wrap for the longer acronyms, and the acronym already
    #: appears in the tile's title, so the group's own symbol reads better.
    GROUP_ICONS = {
        Group.INSTITUTION: "bi-bank",
        Group.PARTNER: "bi-building-fill-check",
        Group.SERVICE: "bi-laptop",
    }

    @property
    def icon(self):
        """Bootstrap-icons class used when the partner has no uploaded logo."""
        return self.GROUP_ICONS.get(self.group, "bi-globe2")
