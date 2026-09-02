from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _


class OrgUnit(models.Model):
    """A node in the ministry's organisational chart (Décret n°2012/644)."""

    class UnitType(models.TextChoices):
        CABINET = "cabinet", _("Cabinet du Ministre")
        INSPECTION = "inspection", _("Inspection Générale")
        SECRETARIAT_GENERAL = "secretariat_general", _("Secrétariat Général")
        DIVISION = "division", _("Division")
        DIRECTION = "direction", _("Direction")
        SOUS_DIRECTION = "sous_direction", _("Sous-direction")
        CELLULE = "cellule", _("Cellule")
        SERVICE = "service", _("Service")
        BUREAU = "bureau", _("Bureau")

    name = models.CharField(_("nom"), max_length=250)
    unit_type = models.CharField(_("type"), max_length=20, choices=UnitType.choices)
    parent = models.ForeignKey(
        "self",
        verbose_name=_("unité parente"),
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="children",
    )
    head_title = models.CharField(
        _("responsable"), max_length=150, blank=True, help_text=_("Ex : Chef de Division")
    )
    mission = models.TextField(_("attributions"), blank=True)
    legal_reference = models.CharField(
        _("référence légale"), max_length=100, blank=True, help_text=_("Ex : Article 25")
    )
    order = models.PositiveIntegerField(_("ordre"), default=0)
    slug = models.SlugField(
        _("slug"), max_length=270, unique=True, null=True, blank=True,
        help_text=_("Généré automatiquement pour les directions ; sert à leur page dédiée."),
    )
    director_name = models.CharField(
        _("nom du responsable actuel"),
        max_length=150,
        blank=True,
        help_text=_("Nom de la personne occupant actuellement ce poste — à tenir à jour par le Ministère."),
    )
    director_email = models.EmailField(_("courriel du responsable"), blank=True)

    class Meta:
        verbose_name = _("unité organisationnelle")
        verbose_name_plural = _("organigramme")
        ordering = ["order", "id"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.unit_type == self.UnitType.DIRECTION and not self.slug:
            base = slugify(self.name)[:260] or "direction"
            slug = base
            suffix = 2
            while OrgUnit.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base}-{suffix}"
                suffix += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        if self.unit_type == self.UnitType.DIRECTION and self.slug:
            return reverse("structures:directorate_detail", kwargs={"slug": self.slug})
        return reverse("structures:org_chart")


class Region(models.Model):
    """One of Cameroon's ten administrative regions."""

    name = models.CharField(_("nom"), max_length=100, unique=True)
    capital = models.CharField(_("chef-lieu"), max_length=100)

    class Meta:
        verbose_name = _("région")
        verbose_name_plural = _("régions")
        ordering = ["name"]

    def __str__(self):
        return self.name


class Delegation(models.Model):
    """Regional or departmental decentralised office of the ministry."""

    class Level(models.TextChoices):
        REGIONAL = "regional", _("Délégation Régionale")
        DEPARTMENTAL = "departmental", _("Délégation Départementale")

    level = models.CharField(_("niveau"), max_length=20, choices=Level.choices)
    region = models.ForeignKey(
        Region, verbose_name=_("région"), on_delete=models.CASCADE, related_name="delegations"
    )
    department_name = models.CharField(_("département"), max_length=100, blank=True)
    town = models.CharField(_("ville"), max_length=100)
    address = models.CharField(_("adresse"), max_length=250, blank=True)
    phone = models.CharField(_("téléphone"), max_length=50, blank=True)
    email = models.EmailField(_("courriel"), blank=True)
    delegate_name = models.CharField(
        _("délégué(e)"),
        max_length=150,
        blank=True,
        help_text=_("À renseigner par le Ministère."),
    )

    class Meta:
        verbose_name = _("délégation")
        verbose_name_plural = _("délégations")
        ordering = ["region__name", "department_name"]

    def __str__(self):
        if self.level == self.Level.REGIONAL:
            return f"{_('Délégation Régionale')} — {self.region.name}"
        return f"{_('Délégation Départementale')} — {self.department_name}"


class TrainingCenter(models.Model):
    """A public or private vocational-training / apprenticeship centre."""

    class CenterType(models.TextChoices):
        CFPE = "cfpe", _("Centre de Formation Professionnelle d'Excellence (CFPE)")
        CSFP = "csfp", _("Centre Sectoriel de Formation Professionnelle (CSFP)")
        CFM = "cfm", _("Centre de Formation aux Métiers (CFM)")
        CAP = "cap", _("Centre d'Apprentissage Professionnel (CAP)")
        CPFPR = "cpfpr", _("Centre Public de Formation Professionnelle Rapide (CPFPR)")
        SARSM = "sarsm", _("Section Artisanale Rurale / Section Ménagère (SAR/SM)")
        CNFFDP = "cnffdp", _("Centre National de Formation des Formateurs et de Développement des Programmes")
        PRIVATE = "private", _("Centre privé agréé")

    class Category(models.TextChoices):
        """How a *public* centre is browsed/filtered on the directory —
        orthogonal to CenterType, which keeps the centre's precise official
        designation (CFPE, CSFP…). Left blank for private centres, which are
        filtered by division instead."""

        NATIONAL = "national", _("Centre national")
        REGIONAL = "regional", _("Centre régional")
        REFERENCE = "reference", _("Centre de référence")
        DIVISIONAL = "divisional", _("Centre divisionnaire")
        SARSM = "sarsm", _("SAR/SM")

    name = models.CharField(_("nom"), max_length=250)
    center_type = models.CharField(_("type de centre"), max_length=20, choices=CenterType.choices)
    is_public = models.BooleanField(_("structure publique"), default=True)
    category = models.CharField(
        _("catégorie"),
        max_length=20,
        choices=Category.choices,
        blank=True,
        help_text=_("Structures publiques uniquement — sert au filtrage de l'annuaire."),
    )
    division = models.CharField(
        _("division"),
        max_length=100,
        blank=True,
        help_text=_("Structures privées uniquement — sert au filtrage de l'annuaire par division."),
    )
    region = models.ForeignKey(
        Region, verbose_name=_("région"), on_delete=models.SET_NULL, null=True, related_name="training_centers"
    )
    town = models.CharField(_("ville"), max_length=100)
    address = models.CharField(_("adresse"), max_length=250, blank=True)
    phone = models.CharField(_("téléphone"), max_length=50, blank=True)
    email = models.EmailField(_("courriel"), blank=True)
    specialties = models.TextField(
        _("filières de formation"), blank=True, help_text=_("Liste séparée par des virgules")
    )
    description = models.TextField(_("description"), blank=True)

    class Meta:
        verbose_name = _("centre de formation")
        verbose_name_plural = _("centres de formation")
        ordering = ["region__name", "town", "name"]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("structures:training_center_detail", kwargs={"pk": self.pk})

    @property
    def specialty_list(self):
        return [s.strip() for s in self.specialties.split(",") if s.strip()]


class AttachedBody(models.Model):
    """An organisation, programme or project attached to the ministry.

    Covers both the bodies placed under the Ministry's supervision (Titre VIII
    du décret n° 2012/644) and the programmes and projects it steers.
    """

    class Kind(models.TextChoices):
        BODY = "body", _("Organisme rattaché")
        PROGRAMME = "programme", _("Programme ou projet")

    name = models.CharField(_("nom"), max_length=250)
    acronym = models.CharField(_("sigle"), max_length=30, blank=True)
    kind = models.CharField(
        _("nature"), max_length=20, choices=Kind.choices, default=Kind.BODY
    )
    description = models.TextField(_("description"), blank=True)
    website = models.URLField(_("site web"), blank=True)
    order = models.PositiveIntegerField(_("ordre"), default=0)

    class Meta:
        verbose_name = _("organisme, programme ou projet")
        verbose_name_plural = _("organismes, programmes et projets")
        ordering = ["order", "name"]

    def __str__(self):
        return f"{self.name} ({self.acronym})" if self.acronym else self.name
