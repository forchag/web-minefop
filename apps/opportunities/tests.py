from datetime import date, timedelta

from django.test import TestCase
from django.urls import reverse
from django.utils.html import escape

from .models import Opportunity


class OpportunityModelTests(TestCase):
    def test_is_open_true_when_no_deadline(self):
        opportunity = Opportunity.objects.create(
            title="Poste ouvert",
            slug="poste-ouvert",
            organisme="MINEFOP",
            summary="Résumé.",
            description="Description.",
        )
        self.assertTrue(opportunity.is_open)

    def test_is_open_false_after_deadline(self):
        opportunity = Opportunity.objects.create(
            title="Concours clôturé",
            slug="concours-cloture",
            kind=Opportunity.Kind.CONCOURS,
            organisme="CNFFDP",
            summary="Résumé.",
            description="Description.",
            application_deadline=date.today() - timedelta(days=1),
        )
        self.assertFalse(opportunity.is_open)

    def test_is_open_true_before_deadline(self):
        opportunity = Opportunity.objects.create(
            title="Concours ouvert",
            slug="concours-ouvert",
            kind=Opportunity.Kind.CONCOURS,
            organisme="CNFFDP",
            summary="Résumé.",
            description="Description.",
            application_deadline=date.today() + timedelta(days=30),
        )
        self.assertTrue(opportunity.is_open)


class OpportunityViewTests(TestCase):
    def setUp(self):
        self.job = Opportunity.objects.create(
            title="Recrutement d'agents",
            slug="recrutement-agents",
            kind=Opportunity.Kind.JOB,
            organisme="MINEFOP",
            summary="Recrutement d'agents contractuels.",
            description="Description détaillée.",
        )
        self.concours = Opportunity.objects.create(
            title="Concours d'entrée",
            slug="concours-entree",
            kind=Opportunity.Kind.CONCOURS,
            organisme="CNFFDP",
            summary="Concours d'entrée en formation.",
            description="Description détaillée.",
        )
        self.draft = Opportunity.objects.create(
            title="Brouillon",
            slug="brouillon-opportunite",
            organisme="MINEFOP",
            summary="Résumé.",
            description="Description.",
            is_published=False,
        )

    def test_list_shows_only_published(self):
        response = self.client.get(reverse("opportunities:list"))
        self.assertContains(response, escape(self.job.title))
        self.assertContains(response, escape(self.concours.title))
        self.assertNotContains(response, escape(self.draft.title))

    def test_list_filters_by_kind(self):
        response = self.client.get(reverse("opportunities:list"), {"type": "concours"})
        self.assertContains(response, escape(self.concours.title))
        self.assertNotContains(response, escape(self.job.title))

    def test_detail_shows_published_opportunity(self):
        response = self.client.get(reverse("opportunities:detail", kwargs={"slug": self.job.slug}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, escape(self.job.title))
        self.assertContains(response, self.job.organisme)

    def test_detail_404s_for_unpublished(self):
        response = self.client.get(reverse("opportunities:detail", kwargs={"slug": self.draft.slug}))
        self.assertEqual(response.status_code, 404)
