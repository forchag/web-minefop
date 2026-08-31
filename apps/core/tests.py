"""Smoke tests for the public pages, the crawler files and the site search."""

import re

from django.test import TestCase
from django.urls import reverse

from apps.core.models import PartnerSite
from apps.documents.models import Document, DocumentCategory
from apps.news.models import Article
from apps.structures.models import AttachedBody, Region, TrainingCenter


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
            excerpt="Un programme national pour l'insertion professionnelle.",
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


class EntryPortalTests(TestCase):
    """The root of the domain serves the bilingual entry portal, not a redirect."""

    @classmethod
    def setUpTestData(cls):
        cls.institution = PartnerSite.objects.create(
            name="Présidence de la République du Cameroun",
            acronym="PRC",
            group=PartnerSite.Group.INSTITUTION,
            url="https://www.prc.cm",
        )
        cls.service = PartnerSite.objects.create(
            name="Inserjeune — suivi post-formation",
            acronym="Inserjeune",
            group=PartnerSite.Group.SERVICE,
            url="https://app.inserjeune.edu.cm",
        )
        cls.unpublished = PartnerSite.objects.create(
            name="Projet Intégré d'Appui aux Acteurs du Secteur Informel",
            acronym="PIAASI",
            group=PartnerSite.Group.PARTNER,
        )
        cls.hidden = PartnerSite.objects.create(
            name="Structure retirée du portail",
            acronym="OFF",
            group=PartnerSite.Group.PARTNER,
            url="https://example.cm",
            is_active=False,
        )

    def test_the_root_url_serves_the_portal_without_redirecting(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "core/portal.html")

    def test_the_portal_opens_both_language_versions(self):
        body = self.client.get("/").content.decode()
        self.assertIn('href="/fr/"', body)
        self.assertIn('href="/en/"', body)

    def test_the_portal_lists_active_partner_sites_by_group(self):
        response = self.client.get("/")
        self.assertContains(response, self.institution.url)
        self.assertContains(response, self.service.url)
        # A partner without a website is still listed, as a non-clickable tile.
        self.assertContains(response, "PIAASI")
        self.assertContains(response, "Site en cours de publication")
        self.assertNotContains(response, self.hidden.name)

    def test_the_portal_loads_no_asset_from_a_third_party(self):
        """Scripts, stylesheets and images must all come from this domain."""
        body = self.client.get("/").content.decode()
        assets = re.findall(r'\ssrc="([^"]+)"', body)
        assets += re.findall(r'<link[^>]+rel="(?:stylesheet|icon|apple-touch-icon|preload)"[^>]+href="([^"]+)"', body)
        self.assertTrue(assets)
        for asset in assets:
            with self.subTest(asset=asset):
                self.assertTrue(asset.startswith("/"), f"{asset} is not served from this domain")


class DocumentDownloadTests(TestCase):
    """Documents may be uploaded or still hosted at their original address."""

    @classmethod
    def setUpTestData(cls):
        cls.category = DocumentCategory.objects.create(name="Référentiels de formation", slug="referentiels")

    def test_an_uploaded_file_takes_precedence_over_the_legacy_address(self):
        document = Document.objects.create(
            title="Référentiel de formation — Maçon",
            category=self.category,
            file="documents/macon.pdf",
            source_url="https://minefop.cm/images/VAGUE1/MACON.pdf",
        )
        self.assertEqual(document.download_url, document.file.url)

    def test_a_document_without_a_file_falls_back_to_its_source_url(self):
        document = Document.objects.create(
            title="Référentiel de formation — Apiculteur",
            category=self.category,
            source_url="https://minefop.cm/images/VAGUE%203/Apiculteur.pdf",
        )
        self.assertEqual(document.download_url, document.source_url)

    def test_the_documents_page_links_a_legacy_hosted_document(self):
        document = Document.objects.create(
            title="Annuaire de la formation professionnelle 2024-2025",
            category=self.category,
            source_url="https://minefop.cm/images/annuaire.pdf",
        )
        response = self.client.get(reverse("documents:list"))
        self.assertContains(response, document.source_url)


class LegacyLibraryTests(TestCase):
    """The catalogue carried over from the previous site must stay well-formed."""

    def test_every_entry_points_at_a_pdf_under_the_ministry_domain(self):
        from apps.documents.legacy_library import LEGACY, OTHER_DOCUMENTS, REFERENTIALS

        self.assertTrue(LEGACY.startswith("https://minefop.cm/"))
        fragments = [fragment for _title, _reference, fragment in REFERENTIALS]
        fragments += [fragment for _slug, _title, _reference, fragment in OTHER_DOCUMENTS]
        self.assertGreater(len(fragments), 90)
        for fragment in fragments:
            with self.subTest(fragment=fragment):
                self.assertTrue(fragment.lower().endswith(".pdf"))

    def test_the_catalogue_holds_no_duplicate_files(self):
        from apps.documents.legacy_library import OTHER_DOCUMENTS, REFERENTIALS

        fragments = [fragment for _title, _reference, fragment in REFERENTIALS]
        fragments += [fragment for _slug, _title, _reference, fragment in OTHER_DOCUMENTS]
        self.assertEqual(len(fragments), len(set(fragments)))

    def test_other_documents_only_use_known_categories(self):
        from apps.documents.legacy_library import OTHER_DOCUMENTS

        known = {"decisions", "communiques", "formulaires", "publications", "rapports"}
        self.assertEqual({slug for slug, _t, _r, _f in OTHER_DOCUMENTS} - known, set())


class AttachedBodyPageTests(TestCase):
    """Bodies under supervision and steered programmes are listed separately."""

    @classmethod
    def setUpTestData(cls):
        cls.body = AttachedBody.objects.create(
            name="Observatoire National de l'Emploi et de la Formation Professionnelle",
            acronym="ONEFOP",
            kind=AttachedBody.Kind.BODY,
        )
        cls.programme = AttachedBody.objects.create(
            name="Projet d'Appui au Développement de l'Enseignement Secondaire et des Compétences",
            acronym="PADESCE",
            kind=AttachedBody.Kind.PROGRAMME,
        )

    def test_both_sections_are_rendered(self):
        response = self.client.get(reverse("structures:attached_bodies"))
        self.assertEqual(list(response.context["bodies"]), [self.body])
        self.assertEqual(list(response.context["programmes"]), [self.programme])
        self.assertContains(response, "ONEFOP")
        self.assertContains(response, "PADESCE")
