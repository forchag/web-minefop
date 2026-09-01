from django.db import migrations

# Cameroon's 58 administrative divisions ("départements"), grouped by region,
# each with its chef-lieu (main town). Kept here rather than imported from
# seed_data.py because migrations should not depend on application code that
# can change independently of the historical model state they operate on.
DIVISIONS_BY_REGION = {
    "Adamaoua": [
        ("Djérem", "Tibati"),
        ("Faro-et-Déo", "Tignère"),
        ("Mayo-Banyo", "Banyo"),
        ("Mbéré", "Meiganga"),
        ("Vina", "Ngaoundéré"),
    ],
    "Centre": [
        ("Haute-Sanaga", "Nanga-Eboko"),
        ("Lekié", "Monatélé"),
        ("Mbam-et-Inoubou", "Bafia"),
        ("Mbam-et-Kim", "Ntui"),
        ("Méfou-et-Afamba", "Mfou"),
        ("Méfou-et-Akono", "Ngoumou"),
        ("Mfoundi", "Yaoundé"),
        ("Nyong-et-Kéllé", "Éséka"),
        ("Nyong-et-Mfoumou", "Akonolinga"),
        ("Nyong-et-So'o", "Mbalmayo"),
    ],
    "Est": [
        ("Boumba-et-Ngoko", "Yokadouma"),
        ("Haut-Nyong", "Abong-Mbang"),
        ("Kadey", "Batouri"),
        ("Lom-et-Djérem", "Bertoua"),
    ],
    "Extrême-Nord": [
        ("Diamaré", "Maroua"),
        ("Logone-et-Chari", "Kousséri"),
        ("Mayo-Danay", "Yagoua"),
        ("Mayo-Kani", "Kaélé"),
        ("Mayo-Sava", "Mora"),
        ("Mayo-Tsanaga", "Mokolo"),
    ],
    "Littoral": [
        ("Moungo", "Nkongsamba"),
        ("Nkam", "Yabassi"),
        ("Sanaga-Maritime", "Édéa"),
        ("Wouri", "Douala"),
    ],
    "Nord": [
        ("Bénoué", "Garoua"),
        ("Faro", "Poli"),
        ("Mayo-Louti", "Guider"),
        ("Mayo-Rey", "Tcholliré"),
    ],
    "Nord-Ouest": [
        ("Boyo", "Fundong"),
        ("Bui", "Kumbo"),
        ("Donga-Mantung", "Nkambe"),
        ("Menchum", "Wum"),
        ("Mezam", "Bamenda"),
        ("Momo", "Mbengwi"),
        ("Ngo-Ketunjia", "Ndop"),
    ],
    "Ouest": [
        ("Bamboutos", "Mbouda"),
        ("Haut-Nkam", "Bafang"),
        ("Hauts-Plateaux", "Baham"),
        ("Koung-Khi", "Bandjoun"),
        ("Menoua", "Dschang"),
        ("Mifi", "Bafoussam"),
        ("Ndé", "Bangangté"),
        ("Noun", "Foumban"),
    ],
    "Sud": [
        ("Dja-et-Lobo", "Sangmélima"),
        ("Mvila", "Ebolowa"),
        ("Océan", "Kribi"),
        ("Vallée-du-Ntem", "Ambam"),
    ],
    "Sud-Ouest": [
        ("Fako", "Limbé"),
        ("Koupé-Manengouba", "Bangem"),
        ("Lebialem", "Menji"),
        ("Manyu", "Mamfe"),
        ("Meme", "Kumba"),
        ("Ndian", "Mundemba"),
    ],
}


def seed_divisions(apps, schema_editor):
    """The site launched with only one delegation per region (the regional
    office) — clicking a region never showed its divisions because none
    existed. Add them now; get_or_create keeps this safe to re-run."""
    Region = apps.get_model("structures", "Region")
    Delegation = apps.get_model("structures", "Delegation")
    for region_name, divisions in DIVISIONS_BY_REGION.items():
        try:
            region = Region.objects.get(name=region_name)
        except Region.DoesNotExist:
            continue
        for department_name, chef_lieu in divisions:
            Delegation.objects.get_or_create(
                region=region,
                level="departmental",
                department_name=department_name,
                defaults={"town": chef_lieu},
            )


def remove_divisions(apps, schema_editor):
    Delegation = apps.get_model("structures", "Delegation")
    Delegation.objects.filter(level="departmental").delete()


class Migration(migrations.Migration):

    dependencies = [
        ("structures", "0005_secretariat_general_unit_type"),
    ]

    operations = [
        migrations.RunPython(seed_divisions, remove_divisions),
    ]
