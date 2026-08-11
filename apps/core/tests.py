"""Smoke tests for the public pages, the crawler files and the site search."""

from django.test import TestCase
from django.urls import reverse

from apps.documents.models import Document, DocumentCategory
from apps.news.models import Article
from apps.structures.models import Region, TrainingCenter


class PublicPagesTests(TestCase):
    """Every public URL must answer 200 in both official languages."""

    VIEW_NAMES = [
        "core:home",
        "core:mission",
        "core:history",
        "core:minister",
        "core:vocational_training",
        "core:search",
        "core:legal_notice",
        "core:accessibility",
        "core:sitemap_page",
        "structures:org_chart",
        "structures:attached_bodies",
        "structures:delegations",
        "structures:training_center_list",
        "documents:list",
        "news:list",
        "contact:contact",
    ]

    def test_pages_render_in_french(self):
        for name in self.VIEW_NAMES:
            with self.subTest(view=name):
                self.assertEqual(self.client.get(reverse(name)).status_code, 200)

    def test_pages_render_in_english(self):
        with self.settings(LANGUAGE_CODE="en"):
            for name in self.VIEW_NAMES:
                with self.subTest(view=name):
                    url = reverse(name).replace("/fr/", "/en/", 1)
                    self.assertEqual(self.client.get(url).status_code, 200)

    def test_unknown_page_returns_404(self):
        self.assertEqual(self.client.get("/fr/page-qui-nexiste-pas/").status_code, 404)


class CrawlerFilesTests(TestCase):
    def test_robots_txt_points_at_the_sitemap_and_shields_the_admin(self):
        response = self.client.get("/robots.txt")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "text/plain; charset=utf-8")
        body = response.content.decode()
        self.assertIn("Disallow: /admin/", body)
        self.assertIn("/sitemap.xml", body)

    def test_sitemap_lists_the_institutional_pages(self):
        response = self.client.get("/sitemap.xml")
        self.assertEqual(response.status_code, 200)
        self.assertIn(reverse("core:mission"), response.content.decode())


class SearchTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        region = Region.objects.create(name="Centre", capital="Yaoundé")
        cls.center = TrainingCenter.objects.create(
            name="Centre de Formation Professionnelle Rapide de Yaoundé",
            center_type=TrainingCenter.CenterType.CPFPR,
            region=region,
            town="Yaoundé",
            specialties="Soudure, Menuiserie",
        )
        cls.article = Article.objects.create(
            title="Lancement du programme JEME",
            slug="lancement-du-programme-jeme",
            excerpt="Un programme national pour l'insertion des jeunes.",
            body="Le programme a été lancé au CNFFDP.",
        )
        category = DocumentCategory.objects.create(name="Lois", slug="lois")
        cls.document = Document.objects.create(
            title="Loi régissant la formation professionnelle",
            category=category,
            reference_number="Loi n° 2018/010 du 11 juillet 2018",
            file="documents/loi-2018-010.pdf",
        )

    def test_search_finds_matches_across_every_content_type(self):
        for term, expected in [
            ("JEME", self.article.title),
            ("2018/010", self.document.title),
            ("Soudure", self.center.name),
        ]:
            with self.subTest(term=term):
                response = self.client.get(reverse("core:search"), {"q": term})
                self.assertEqual(response.status_code, 200)
                self.assertContains(response, expected)

    def test_search_without_a_query_prompts_instead_of_listing_everything(self):
        response = self.client.get(reverse("core:search"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["result_count"], 0)
        self.assertNotContains(response, self.article.title)

    def test_search_reports_when_nothing_matches(self):
        response = self.client.get(reverse("core:search"), {"q": "zzzzzzz"})
        self.assertEqual(response.context["result_count"], 0)
