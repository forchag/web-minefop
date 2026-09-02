from django.test import TestCase
from django.urls import reverse

from .models import Delegation, OrgUnit, Region, TrainingCenter


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


class DivisionsShowUpAfterSelectingARegionTests(TestCase):
    """Selecting a region used to only ever show its single regional
    delegation — there were no departmental (division) delegations at all."""

    def setUp(self):
        self.region = Region.objects.create(name="Centre", capital="Yaoundé")
        Delegation.objects.create(
            level=Delegation.Level.REGIONAL, region=self.region, town="Yaoundé"
        )
        Delegation.objects.create(
            level=Delegation.Level.DEPARTMENTAL,
            region=self.region,
            department_name="Mfoundi",
            town="Yaoundé",
        )

    def test_selecting_a_region_shows_its_divisions(self):
        response = self.client.get(reverse("structures:delegations"), {"region": self.region.pk})
        self.assertContains(response, "Mfoundi")
        self.assertContains(response, "Délégation Départementale")


class SeedDivisionsMigrationTests(TestCase):
    """The database launched with only one delegation per region — this
    migration is what backfills the 58 divisions onto an already-seeded
    (pre-existing) production database."""

    def setUp(self):
        import importlib

        self.migration_module = importlib.import_module(
            "apps.structures.migrations.0006_seed_divisions"
        )
        for name, capital in [("Centre", "Yaoundé"), ("Littoral", "Douala")]:
            Region.objects.create(name=name, capital=capital)

    def test_seeding_creates_every_division_for_every_known_region(self):
        from django.apps import apps

        self.migration_module.seed_divisions(apps, None)
        self.assertEqual(
            Delegation.objects.filter(level=Delegation.Level.DEPARTMENTAL).count(),
            len(self.migration_module.DIVISIONS_BY_REGION["Centre"])
            + len(self.migration_module.DIVISIONS_BY_REGION["Littoral"]),
        )
        self.assertTrue(
            Delegation.objects.filter(department_name="Mfoundi", region__name="Centre").exists()
        )

    def test_seeding_twice_does_not_duplicate(self):
        from django.apps import apps

        self.migration_module.seed_divisions(apps, None)
        self.migration_module.seed_divisions(apps, None)
        self.assertEqual(
            Delegation.objects.filter(department_name="Mfoundi").count(), 1
        )

    def test_all_58_cameroonian_divisions_are_accounted_for(self):
        total = sum(len(divisions) for divisions in self.migration_module.DIVISIONS_BY_REGION.values())
        self.assertEqual(total, 58)


class TrainingCenterDirectoryTests(TestCase):
    """The directory is split public/private: public centres are filtered
    by category (national/regional/reference/divisional/SAR-SM), private
    ones by division instead."""

    def setUp(self):
        self.region = Region.objects.create(name="Centre", capital="Yaoundé")
        self.national_center = TrainingCenter.objects.create(
            name="Centre Pilote National de Test",
            center_type=TrainingCenter.CenterType.CNFFDP,
            category=TrainingCenter.Category.NATIONAL,
            is_public=True,
            region=self.region,
            town="Yaoundé",
        )
        self.divisional_center = TrainingCenter.objects.create(
            name="CPFPR de Yaoundé",
            center_type=TrainingCenter.CenterType.CPFPR,
            category=TrainingCenter.Category.DIVISIONAL,
            is_public=True,
            region=self.region,
            town="Yaoundé",
        )
        self.private_center = TrainingCenter.objects.create(
            name="Institut Privé de Formation de Mfoundi",
            center_type=TrainingCenter.CenterType.PRIVATE,
            is_public=False,
            division="Mfoundi",
            region=self.region,
            town="Yaoundé",
        )

    def test_default_view_shows_only_public_centres(self):
        response = self.client.get(reverse("structures:training_center_list"))
        self.assertContains(response, "Centre Pilote National de Test")
        self.assertContains(response, "CPFPR de Yaoundé")
        self.assertNotContains(response, "Institut Privé de Formation de Mfoundi")

    def test_private_ownership_shows_only_private_centres(self):
        response = self.client.get(reverse("structures:training_center_list"), {"ownership": "private"})
        self.assertContains(response, "Institut Privé de Formation de Mfoundi")
        self.assertNotContains(response, "Centre Pilote National de Test")
        self.assertNotContains(response, "CPFPR de Yaoundé")

    def test_public_centres_are_filterable_by_category(self):
        response = self.client.get(
            reverse("structures:training_center_list"),
            {"ownership": "public", "category": TrainingCenter.Category.NATIONAL},
        )
        self.assertContains(response, "Centre Pilote National de Test")
        self.assertNotContains(response, "CPFPR de Yaoundé")

    def test_private_centres_are_filterable_by_division(self):
        response = self.client.get(
            reverse("structures:training_center_list"),
            {"ownership": "private", "division": "Mfoundi"},
        )
        self.assertContains(response, "Institut Privé de Formation de Mfoundi")

        other_division_response = self.client.get(
            reverse("structures:training_center_list"),
            {"ownership": "private", "division": "Wouri"},
        )
        self.assertNotContains(other_division_response, "Institut Privé de Formation de Mfoundi")


class BackfillTrainingCenterCategoryMigrationTests(TestCase):
    """Existing public centres were seeded with only a center_type — this
    migration is what backfills the new category filter field for them on
    an already-seeded database."""

    def test_backfill_maps_every_center_type_to_the_right_category(self):
        import importlib

        migration_module = importlib.import_module(
            "apps.structures.migrations.0007_training_center_category_and_division"
        )
        region = Region.objects.create(name="Centre", capital="Yaoundé")
        centers = {
            center_type: TrainingCenter.objects.create(
                name=center_type, center_type=center_type, region=region, town="Yaoundé"
            )
            for center_type in migration_module.CATEGORY_BY_CENTER_TYPE
        }

        from django.apps import apps

        migration_module.backfill_category(apps, None)

        for center_type, center in centers.items():
            center.refresh_from_db()
            self.assertEqual(center.category, migration_module.CATEGORY_BY_CENTER_TYPE[center_type])
