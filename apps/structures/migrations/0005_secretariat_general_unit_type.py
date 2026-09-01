from django.db import migrations, models


def fix_secretariat_general_type(apps, schema_editor):
    """The Secrétariat Général was originally seeded as unit_type="direction",
    which wrongly listed it among the ministry's directorates (it sits above
    them, coordinating their work, not alongside them). Retroactively fix any
    database seeded before this distinction existed."""
    OrgUnit = apps.get_model("structures", "OrgUnit")
    OrgUnit.objects.filter(
        name="Secrétariat Général", unit_type="direction"
    ).update(unit_type="secretariat_general")


def revert_secretariat_general_type(apps, schema_editor):
    OrgUnit = apps.get_model("structures", "OrgUnit")
    OrgUnit.objects.filter(
        name="Secrétariat Général", unit_type="secretariat_general"
    ).update(unit_type="direction")


class Migration(migrations.Migration):

    dependencies = [
        ("structures", "0004_backfill_directorate_slugs"),
    ]

    operations = [
        migrations.AlterField(
            model_name="orgunit",
            name="unit_type",
            field=models.CharField(
                choices=[
                    ("cabinet", "Cabinet du Ministre"),
                    ("inspection", "Inspection Générale"),
                    ("secretariat_general", "Secrétariat Général"),
                    ("division", "Division"),
                    ("direction", "Direction"),
                    ("sous_direction", "Sous-direction"),
                    ("cellule", "Cellule"),
                    ("service", "Service"),
                    ("bureau", "Bureau"),
                ],
                max_length=20,
                verbose_name="type",
            ),
        ),
        migrations.RunPython(fix_secretariat_general_type, revert_secretariat_general_type),
    ]
