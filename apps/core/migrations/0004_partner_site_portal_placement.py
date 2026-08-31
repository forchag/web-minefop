"""Place the existing portal tiles into their columns, with their banner colours.

The columns and tints are new fields, so a site that was already seeded would
otherwise show every tile on the left with the default dark banner. This puts
the directory into the arrangement the portal is meant to carry, and leaves any
entry the Ministry has since added or renamed exactly as it is.
"""

from django.db import migrations

# acronym -> (column, order, tint, shown on the portal)
PLACEMENT = {
    "PRC": ("left", 1, "#27ae60", True),
    "SPM": ("left", 2, "#e74c3c", True),
    "MINJEC": ("left", 3, "#e74c3c", True),
    "ONJ": ("left", 4, "#f39c12", True),
    "CNJC": ("left", 5, "#3498db", True),
    "JobHub": ("left", 6, "#3498db", True),
    "FNE": ("right", 1, "#16a085", True),
    "ONEFOP": ("right", 2, "#d35400", True),
    "PIAASI": ("right", 3, "#9b59b6", True),
    "CIOP": ("right", 4, "#34495e", True),
    "CNFFDP": ("right", 5, "#34495e", True),
    # Kept in the administration, off the portal until the Ministry wants them.
    "PADESCE": ("right", 6, "#34495e", False),
    "SIGE": ("right", 7, "#34495e", False),
    "Inserjeune": ("right", 8, "#34495e", False),
}


def place_tiles(apps, schema_editor):
    PartnerSite = apps.get_model("core", "PartnerSite")
    for acronym, (column, order, tint, is_active) in PLACEMENT.items():
        PartnerSite.objects.filter(acronym=acronym).update(
            column=column, order=order, tint=tint, is_active=is_active
        )


def unplace_tiles(apps, schema_editor):
    """Reverse: clear the colours and show everything again, on the left."""
    PartnerSite = apps.get_model("core", "PartnerSite")
    PartnerSite.objects.filter(acronym__in=PLACEMENT).update(
        column="left", tint="", is_active=True
    )


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0003_alter_partnersite_options_partnersite_column_and_more"),
    ]

    operations = [
        migrations.RunPython(place_tiles, unplace_tiles),
    ]
