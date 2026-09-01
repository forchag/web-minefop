from django.db import models
from django.utils.translation import gettext_lazy as _


class PressScope(models.TextChoices):
    """Whether a press release (news article or blog post) covers the whole
    country or a single region — shared so the merged "Communiqués de
    presse" section can filter across both content types consistently."""

    NATIONAL = "national", _("National")
    REGIONAL = "regional", _("Régional")
