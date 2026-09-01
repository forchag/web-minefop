"""Smoke tests for the public pages, the crawler files and the site search."""

import re

from django.test import TestCase
from django.urls import reverse
from django.utils import translation

from apps.core.models import MinisterMessage, PartnerSite
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
        "structures:directorate_list",
        "structures:attached_bodies",
        "structures:delegations",
        "structures:training_center_list",
        "documents:list",
        "media:event_list",
        "media:gallery_list",
        "press:list",
        "opportunities:list",
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
    """The root of the domain serves the bilingual entry portal, not a redirect.

    templates/core/portal.html is currently maintained by hand rather than
    rendered from Sites partenaires: the Ministry replaced the data-driven
    version with a static template (see the "Update portal.html" / "Delete
    MINJEC block from portal.html" commits), and asked for it to stay exactly
    as written. The tests below split accordingly — some exercise PartnerSite
    itself (still real, still used by the admin), others exercise the actual
    markup the page ships today. Editing Sites partenaires in the admin has no
    effect on this page unless portal.html is changed to read it again.
    """

    @classmethod
    def setUpTestData(cls):
        cls.institution = PartnerSite.objects.create(
            name="Présidence de la République du Cameroun",
            acronym="PRC",
            group=PartnerSite.Group.INSTITUTION,
            column=PartnerSite.Column.LEFT,
            order=1,
            tint="#27ae60",
            url="https://www.prc.cm",
        )
        cls.with_supplied_logo = PartnerSite.objects.create(
            name="Fonds National de l'Emploi",
            acronym="FNE",
            group=PartnerSite.Group.PARTNER,
            column=PartnerSite.Column.RIGHT,
            order=1,
            url="https://fnecm.org",
            logo_url="https://fnecm.org/images/stories/lefne7questions/LogoFNEnu.png",
        )
        cls.unpublished = PartnerSite.objects.create(
            name="Projet Intégré d'Appui aux Acteurs du Secteur Informel",
            acronym="PIAASI",
            group=PartnerSite.Group.PARTNER,
            column=PartnerSite.Column.RIGHT,
            order=2,
        )
        cls.hidden = PartnerSite.objects.create(
            name="Structure retirée du portail",
            acronym="OFF",
            group=PartnerSite.Group.PARTNER,
            column=PartnerSite.Column.LEFT,
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

    def test_the_portal_links_to_the_institutions_and_partners_it_currently_lists(self):
        """Locks in today's ten hard-coded tiles so a future edit to
        portal.html is a deliberate, visible diff in this test — not a silent
        loss of a link nobody notices until a visitor reports it missing."""
        response = self.client.get("/")
        for href in [
            "https://www.prc.cm",
            "https://www.spm.gov.cm",
            "https://www.onjcameroun.cm",
            "https://www.cnjcnyc.cm",
            "https://www.cnjcjobhub.cm",
            "https://fnecm.org",
            "https://onefop.cm",
            "https://www.cnffdp.cm",
        ]:
            with self.subTest(href=href):
                self.assertContains(response, href)
        # PIASSI has no site of its own yet (href="#"); CIOP links to a page on
        # this domain (/ciop/) rather than out — both still keep their tile.
        self.assertContains(response, "PIASSI")
        self.assertContains(response, 'href="/ciop/"')
        # Deliberately removed from the portal (see "Delete MINJEC block from
        # portal.html") — still present as an OrgUnit and in Textes & documents.
        self.assertNotContains(response, "MINJEC")
        self.assertNotContains(response, self.hidden.name)

    def test_each_tile_is_placed_in_the_column_it_was_given(self):
        """Which side a tile sits on is recorded per partner, not computed."""
        context = self.client.get("/").context
        self.assertEqual([p.acronym for p in context["left_column"]], ["PRC"])
        self.assertEqual(
            [p.acronym for p in context["right_column"]], ["FNE", "PIAASI"]
        )
        # The hidden entry has a column too, and still stays off the portal.
        self.assertNotIn(self.hidden, list(context["left_column"]))

    def test_a_tile_carries_the_banner_colour_it_was_given(self):
        self.assertEqual(self.institution.tint_rgba, "rgba(39, 174, 96, 0.9)")
        self.assertEqual(self.unpublished.tint_rgba, "")
        self.assertContains(
            self.client.get("/"), 'style="background: rgba(39, 174, 96, 0.9)"'
        )

    def test_a_tile_prefers_a_hosted_logo_then_the_supplied_address(self):
        self.assertEqual(
            self.with_supplied_logo.logo_src, self.with_supplied_logo.logo_url
        )
        self.assertContains(self.client.get("/"), self.with_supplied_logo.logo_url)

    # There is no referrerpolicy or JS acronym-fallback to test here any more:
    # portal.html's <img> tags are now written by hand (see the class
    # docstring) and carry neither. That does mean a structure's own
    # hotlink-protected site, or a dead logo address, will show a browser's
    # default broken-image icon rather than falling back gracefully — worth
    # knowing if a tile ever looks broken on the live page.

    def test_the_portal_loads_its_code_and_type_from_this_domain(self):
        """Scripts, stylesheets, fonts and icons must never come from a third party.

        Partner logos are the one exception: a tile may serve the address the
        structure supplied until that image is mirrored here with
        "manage.py fetch_partner_logos".
        """
        body = self.client.get("/").content.decode()
        assets = re.findall(r'<script[^>]+src="([^"]+)"', body)
        assets += re.findall(
            r'<link[^>]+rel="(?:stylesheet|icon|apple-touch-icon|preload)"[^>]+href="([^"]+)"',
            body,
        )
        self.assertTrue(assets)
        for asset in assets:
            with self.subTest(asset=asset):
                self.assertTrue(asset.startswith("/"), f"{asset} is not served from this domain")

    def test_no_asset_is_loaded_over_plain_http(self):
        """An http:// asset is blocked as mixed content once the site is on https.

        CIOP's logo is still served at http://www.orientation.cm/... in
        portal.html as written — that is the address on record, kept here
        deliberately (see the class docstring) rather than corrected on this
        page's behalf. It is allowlisted below so this test still fails on any
        *other* asset that starts using plain http, which is the regression
        this test exists to catch.
        """
        KNOWN_HTTP_ASSET = "http://www.orientation.cm/wp-content/uploads/2019/06/logo-cosup.png"
        body = self.client.get("/").content.decode()
        for asset in re.findall(r'\ssrc="([^"]+)"', body):
            if asset == KNOWN_HTTP_ASSET:
                continue
            with self.subTest(asset=asset):
                self.assertFalse(asset.startswith("http://"), f"{asset} would be blocked as mixed content")

    def test_a_supplied_logo_address_is_only_used_when_nothing_is_hosted_here(self):
        self.with_supplied_logo.logo = "partners/fne.png"
        self.assertEqual(self.with_supplied_logo.logo_src, self.with_supplied_logo.logo.url)


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

    def test_an_unknown_category_slug_shows_every_document_instead_of_404ing(self):
        document = Document.objects.create(
            title="Référentiel de formation — Soudeur",
            category=self.category,
            source_url="https://minefop.cm/images/soudeur.pdf",
        )
        response = self.client.get(reverse("documents:list"), {"categorie": "not-a-real-category"})
        self.assertEqual(response.status_code, 200)
        self.assertIsNone(response.context["active_category"])
        self.assertContains(response, document.title)


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


class NavbarLinksTests(TestCase):
    """Regression coverage for links embedded directly in the navbar
    template, which aren't exercised by simply visiting every named view."""

    def test_training_texts_link_points_at_a_real_category(self):
        response = self.client.get(reverse("core:home"))
        self.assertContains(response, "?categorie=referentiels")

    def test_opportunities_dropdown_links_to_emploi_jeune(self):
        response = self.client.get(reverse("core:home"))
        self.assertContains(response, "https://emploijeune.cm/")
        self.assertContains(response, "Emploi Jeune")


class MinisterMessageTranslationTests(TestCase):
    def setUp(self):
        self.minister = MinisterMessage.load()
        self.minister.message_fr = "Message en français."
        self.minister.message_en = "Message in English."
        self.minister.save()

    def test_message_follows_active_language(self):
        self.assertEqual(self.minister.message, self.minister.message_fr)
        with translation.override("en"):
            self.assertEqual(self.minister.message, self.minister.message_en)

    def test_message_falls_back_to_french_when_untranslated(self):
        self.minister.message_en = ""
        self.minister.save(update_fields=["message_en"])
        with translation.override("en"):
            self.assertEqual(self.minister.message, self.minister.message_fr)

    def test_minister_page_shows_english_message_under_english_prefix(self):
        with translation.override("en"):
            response = self.client.get(reverse("core:minister"))
        self.assertContains(response, self.minister.message_en)
