"""Record the logo address supplied for each portal tile.

A site seeded before the field existed has no logo address, so its tiles fall
back to the acronym. This fills them in. Entries that already carry an uploaded
file keep serving that file — `PartnerSite.logo_src` prefers it — so this only
changes what a tile shows when nothing has been uploaded for it.
"""

from django.db import migrations

# acronym -> logo address supplied for the portal
LOGO_URLS = {
    "PRC": "https://www.minjec.gov.cm/portail/images/bloc/prc.png",
    "SPM": "https://www.minjec.gov.cm/portail/images/bloc/spm.jpg",
    "MINJEC": "https://minjec.gov.cm/site/wp-content/uploads/2022/10/logo.png",
    "ONJ": "https://www.minjec.gov.cm/portail/images/bloc/onj.png",
    "CNJC": "https://raw.githubusercontent.com/forchag/SOME-PICS/refs/heads/main/new.jpeg",
    "JobHub": "https://raw.githubusercontent.com/forchag/SOME-PICS/refs/heads/main/cnjcnycjoblogo.png",
    "FNE": "https://fnecm.org/images/stories/lefne7questions/LogoFNEnu.png",
    "ONEFOP": "https://onefop.cm/wp-content/uploads/2026/04/WhatsApp-Image-2026-04-07-at-07.43.13.jpeg",
    "PIAASI": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRRdA0liNY2iPRS6czCI_QXUASXGhpUNWkm1wSlw2YE&s=10",
    "CIOP": "https://www.orientation.cm/wp-content/uploads/2019/06/logo-cosup.png",
    "CNFFDP": "https://raw.githubusercontent.com/forchag/SOME-PICS/refs/heads/main/Logo%20CNFFDP.png",
}


def set_logo_urls(apps, schema_editor):
    PartnerSite = apps.get_model("core", "PartnerSite")
    for acronym, url in LOGO_URLS.items():
        PartnerSite.objects.filter(acronym=acronym, logo_url="").update(logo_url=url)


def clear_logo_urls(apps, schema_editor):
    PartnerSite = apps.get_model("core", "PartnerSite")
    PartnerSite.objects.filter(acronym__in=LOGO_URLS).update(logo_url="")


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0005_partnersite_logo_url"),
    ]

    operations = [
        migrations.RunPython(set_logo_urls, clear_logo_urls),
    ]
