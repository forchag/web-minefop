from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class NewsCategory(models.Model):
    name = models.CharField(_("nom"), max_length=100)
    slug = models.SlugField(_("slug"), max_length=110, unique=True)

    class Meta:
        verbose_name = _("catégorie d'actualité")
        verbose_name_plural = _("catégories d'actualités")
        ordering = ["name"]

    def __str__(self):
        return self.name


class Article(models.Model):
    title = models.CharField(_("titre"), max_length=250)
    slug = models.SlugField(_("slug"), max_length=270, unique=True)
    category = models.ForeignKey(
        NewsCategory,
        verbose_name=_("catégorie"),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="articles",
    )
    excerpt = models.CharField(_("chapô"), max_length=300)
    body = models.TextField(_("contenu"))
    cover_image = models.ImageField(_("image de couverture"), upload_to="news/", blank=True, null=True)
    published_at = models.DateTimeField(_("date de publication"), default=timezone.now)
    is_published = models.BooleanField(_("publié"), default=True)

    class Meta:
        verbose_name = _("article")
        verbose_name_plural = _("actualités")
        ordering = ["-published_at"]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("news:detail", kwargs={"slug": self.slug})
