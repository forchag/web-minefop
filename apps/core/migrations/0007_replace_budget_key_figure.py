"""Replace the "Budget 2026 Emploi & Formation Pro." key figure on live sites.

The label and icon were changed in `seed_data.py` a while ago, but
`seed_key_figures()` only runs once per database (`if KeyFigure.objects.exists():
return`), so a site seeded before that change still shows the old, budget-
figure row on its homepage — exactly what was reported. This updates that row
in place rather than requiring a re-seed, which would also duplicate every
other key figure already created.
"""

from django.db import migrations

OLD_LABEL = "Budget 2026 Emploi & Formation Pro."
NEW_LABEL = "Spécialités professionnelles recensées"
NEW_VALUE = "228"
NEW_ICON = "bi-tools"


def replace_budget_figure(apps, schema_editor):
    KeyFigure = apps.get_model("core", "KeyFigure")
    KeyFigure.objects.filter(label__startswith=OLD_LABEL).update(
        label=NEW_LABEL, value=NEW_VALUE, icon=NEW_ICON
    )


def restore_budget_figure(apps, schema_editor):
    """Reverse: only meaningful if nothing has touched the row since."""
    KeyFigure = apps.get_model("core", "KeyFigure")
    KeyFigure.objects.filter(label=NEW_LABEL, value=NEW_VALUE, icon=NEW_ICON).update(
        label=f"{OLD_LABEL} (FCFA)", value="33,4 Mds", icon="bi-cash-coin"
    )


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0006_partner_site_logo_urls"),
    ]

    operations = [
        migrations.RunPython(replace_budget_figure, restore_budget_figure),
    ]
