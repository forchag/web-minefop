from django.core.validators import RegexValidator
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
    message_fr = models.TextField(_("mot du ministre (français)"))
    message_en = models.TextField(_("mot du ministre (anglais)"), blank=True)
    updated_at = models.DateTimeField(_("dernière mise à jour"), auto_now=True)

    class Meta:
        verbose_name = _("mot du ministre")
        verbose_name_plural = _("mot du ministre")

    def __str__(self):
        return str(self.title)

    @property
    def message(self):
        """The message in the currently active site language (fr/en),
        falling back to French if no English translation has been entered
        yet."""
        from django.utils.translation import get_language

        language = get_language() or ""
        if language.startswith("en") and self.message_en:
            return self.message_en
        return self.message_fr

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

    class Column(models.TextChoices):
        LEFT = "left", _("Colonne de gauche")
        RIGHT = "right", _("Colonne de droite")

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
    logo_url = models.URLField(
        _("adresse du logo"),
        max_length=500,
        blank=True,
        help_text=_(
            "Adresse du logo fourni par la structure, utilisée tant qu'aucun "
            "fichier n'a été téléversé ci-dessus. La commande "
            "« fetch_partner_logos » récupère ces images et les héberge sur le "
            "domaine du Ministère."
        ),
    )
    column = models.CharField(
        _("colonne"),
        max_length=10,
        choices=Column.choices,
        default=Column.LEFT,
        help_text=_("Côté du portail où la vignette est placée."),
    )
    tint = models.CharField(
        _("couleur du bandeau"),
        max_length=7,
        blank=True,
        validators=[RegexValidator(r"^#[0-9a-fA-F]{6}$", _("Indiquez une couleur hexadécimale, par exemple #27ae60."))],
        help_text=_(
            "Couleur du bandeau qui porte le nom de la structure, au survol de "
            "la vignette. Ex : #27ae60. Laisser vide pour le fond sombre par défaut."
        ),
    )
    order = models.PositiveIntegerField(_("ordre"), default=0)
    is_active = models.BooleanField(_("affiché sur le portail"), default=True)

    class Meta:
        verbose_name = _("site partenaire")
        verbose_name_plural = _("sites partenaires")
        ordering = ["column", "order", "name"]

    def __str__(self):
        return f"{self.acronym} — {self.name}" if self.acronym else self.name

    @property
    def logo_src(self):
        """Where the tile's logo comes from.

        A file uploaded through the administration wins, because it is served
        from the Ministry's own domain; otherwise the address supplied by the
        structure is used, and failing both the tile falls back to the acronym.
        """
        if self.logo:
            return self.logo.url
        return self.logo_url

    @property
    def tint_rgba(self):
        """The banner colour as the portal draws it: the tint at 90% opacity."""
        if not self.tint:
            return ""
        red, green, blue = (int(self.tint[i : i + 2], 16) for i in (1, 3, 5))
        return f"rgba({red}, {green}, {blue}, 0.9)"

    #: Logos shipped with the project, keyed by acronym. `seed_data` attaches
    #: them so a fresh install shows the real marks; anything uploaded through
    #: the administration afterwards replaces them.
    BUNDLED_LOGOS = {
        "CNFFDP": "cnffdp.png",
        "CNJC": "cnjc.png",
        "JobHub": "cnjc-jobhub.png",
    }
