from django.test import TestCase
from django.urls import reverse

from .models import OrgUnit


class SecretariatGeneralIsNotADirectorateTests(TestCase):
    """The Secrétariat Général coordinates the ministry's directorates from
    above them — it is not itself one, so it must not show up as one."""

    def setUp(self):
        self.minister = OrgUnit.objects.create(name="Cabinet du Ministre", unit_type=OrgUnit.UnitType.CABINET)
        self.sg = OrgUnit.objects.create(
            name="Secrétariat Général",
            unit_type=OrgUnit.UnitType.SECRETARIAT_GENERAL,
            parent=self.minister,
            head_title="Secrétaire Général",
        )
        self.directorate = OrgUnit.objects.create(
            name="Direction de la Régulation de la Main-d'œuvre",
            unit_type=OrgUnit.UnitType.DIRECTION,
            parent=self.minister,
        )

    def test_the_directorate_list_page_excludes_the_secretariat_general(self):
        response = self.client.get(reverse("structures:directorate_list"))
        self.assertContains(response, "Régulation de la Main")
        self.assertNotContains(response, "Secrétariat Général")

    def test_the_org_chart_still_shows_the_secretariat_general(self):
        response = self.client.get(reverse("structures:org_chart"))
        self.assertContains(response, "Secrétariat Général")
