from django.db import migrations
from django.utils.text import slugify


def backfill_slugs(apps, schema_editor):
    """OrgUnit.save() auto-generates a slug for "direction"-type rows going
    forward, but that only fires on save() — an already-seeded database's
    existing directorate rows were never saved after the field was added, so
    they need this one-off backfill (same reasoning as the KeyFigure fix in
    apps.core.migrations.0007)."""
    OrgUnit = apps.get_model("structures", "OrgUnit")
    used_slugs = set(
        OrgUnit.objects.exclude(slug__isnull=True).exclude(slug="").values_list("slug", flat=True)
    )
    for unit in OrgUnit.objects.filter(unit_type="direction", slug__isnull=True):
        base = slugify(unit.name)[:260] or "direction"
        slug = base
        suffix = 2
        while slug in used_slugs:
            slug = f"{base}-{suffix}"
            suffix += 1
        used_slugs.add(slug)
        unit.slug = slug
        unit.save(update_fields=["slug"])


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("structures", "0003_orgunit_director_email_orgunit_director_name_and_more"),
    ]

    operations = [
        migrations.RunPython(backfill_slugs, noop),
    ]
