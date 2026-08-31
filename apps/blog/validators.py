"""Shared upload guards for the blog app.

Kept separate from models.py so the same limits can be reused by both
BlogPost.cover_image and BlogAttachment.file without repeating the numbers.
"""

from django.core.exceptions import ValidationError
from django.template.defaultfilters import filesizeformat
from django.utils.translation import gettext_lazy as _

MAX_UPLOAD_SIZE = 20 * 1024 * 1024  # 20 MB — generous for a scanned PDF, still bounded.


def validate_file_size(file):
    if file.size > MAX_UPLOAD_SIZE:
        raise ValidationError(
            _("Ce fichier (%(size)s) dépasse la taille maximale autorisée de %(max)s.")
            % {"size": filesizeformat(file.size), "max": filesizeformat(MAX_UPLOAD_SIZE)}
        )
