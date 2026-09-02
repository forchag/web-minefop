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
        "core:minister_biography",
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

    def test_opportunities_dropdown_links_to_the_attached_bodies(self):
        response = self.client.get(reverse("core:home"))
        self.assertContains(response, "https://fnecm.org/")
        self.assertContains(response, "FNE")
        self.assertContains(response, "https://onefop.cm/")
        self.assertContains(response, "ONEFOP")
        self.assertContains(response, "https://www.cnffdp.cm/")
        self.assertContains(response, "CNFFDP")

    def test_the_delegations_link_is_now_labelled_deconcentrated_services(self):
        response = self.client.get(reverse("core:home"))
        self.assertContains(response, "Services déconcentrés")

    def test_press_releases_are_now_labelled_actualites(self):
        response = self.client.get(reverse("core:home"))
        self.assertContains(response, "Actualités")
        self.assertNotContains(response, "Communiqués de presse")

    def test_formation_and_emploi_is_folded_into_documents_and_media(self):
        response = self.client.get(reverse("core:home"))
        self.assertNotContains(response, "Formation &amp; Emploi")
        self.assertContains(response, reverse("core:vocational_training"))
        self.assertContains(response, "Le dispositif national de formation")
        self.assertContains(response, "Documents et médias")

    def test_training_centers_navbar_dropdown_links_public_and_private(self):
        response = self.client.get(reverse("core:home"))
        training_center_url = reverse("structures:training_center_list")
        self.assertContains(response, f"{training_center_url}?ownership=public")
        self.assertContains(response, f"{training_center_url}?ownership=private")
        self.assertContains(response, "Centres publics")
        self.assertContains(response, "Centres privés agréés")


class HomePageFivePillarsTests(TestCase):
    """The hero and the section right under it were rewritten around the
    ministry's five pillars: orientation, formation, insertion, emploi and
    entrepreneuriat."""

    def test_hero_reflects_the_five_pillars(self):
        response = self.client.get(reverse("core:home"))
        self.assertContains(response, "Orientation, formation, insertion, emploi, entrepreneuriat")

    def test_each_pillar_links_to_its_page(self):
        response = self.client.get(reverse("core:home"))
        content = response.content.decode()
        for label in ["Orientation", "Formation", "Insertion", "Emploi", "Entrepreneuriat"]:
            self.assertIn(label, content)
        self.assertContains(response, reverse("core:vocational_training"))
        self.assertContains(response, reverse("structures:training_center_list"))
        self.assertContains(response, reverse("opportunities:list"))
        self.assertContains(response, reverse("structures:attached_bodies"))


class HeroSidebarTests(TestCase):
    """The hero's side column dropped the big static MINEFOP logo in favour
    of a minister teaser and a short upcoming-events agenda, matching the
    layout used on other ministries' home pages."""

    def test_the_big_logo_is_gone(self):
        response = self.client.get(reverse("core:home"))
        self.assertNotContains(response, "Logo du MINEFOP")
        self.assertNotContains(response, 'width="230" height="297"')

    def test_the_minister_teaser_links_to_the_full_message(self):
        response = self.client.get(reverse("core:home"))
        self.assertContains(response, reverse("core:minister"))
        self.assertContains(response, "Mot du Ministre")

    def test_an_upcoming_event_appears_in_the_agenda(self):
        from datetime import timedelta

        from django.utils import timezone

        from apps.media.models import Event

        upcoming = Event.objects.create(
            title="Journée portes ouvertes des centres de formation",
            slug="journee-portes-ouvertes",
            description="Description.",
            start_at=timezone.now() + timedelta(days=5),
        )
        past = Event.objects.create(
            title="Événement déjà passé",
            slug="evenement-passe",
            description="Description.",
            start_at=timezone.now() - timedelta(days=5),
        )
        response = self.client.get(reverse("core:home"))
        self.assertContains(response, upcoming.title)
        self.assertNotContains(response, past.title)

    def test_agenda_shows_a_message_when_no_events_are_upcoming(self):
        response = self.client.get(reverse("core:home"))
        self.assertContains(response, "Aucun événement à venir pour le moment.")


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


class HumanizedMinisterMessageMigrationTests(TestCase):
    """0011 dropped the minister's personal biography and dated history in
    favour of a generic, mission-focused message."""

    def setUp(self):
        import importlib

        self.migration_module = importlib.import_module(
            "apps.core.migrations.0011_humanize_minister_message"
        )

    def test_the_new_message_has_no_em_dashes(self):
        self.assertNotIn("—", self.migration_module.NEW_FRENCH_MESSAGE)
        self.assertNotIn("—", self.migration_module.NEW_ENGLISH_MESSAGE)

    def test_the_new_message_drops_the_personal_biography(self):
        for phrase in ["Ingénieur de formation", "Secrétaire d'État", "juin 2025", "novembre 2025"]:
            self.assertNotIn(phrase, self.migration_module.NEW_FRENCH_MESSAGE)


class MinisterMessageStyleRewriteMigrationTests(TestCase):
    """0012 restyled the message on the register of real Cameroonian
    ministerial addresses (a presidential-priority framing and a quotable
    programme phrase), while keeping it generic, free of personal history,
    and covering the five pillars."""

    def setUp(self):
        import importlib

        self.migration_module = importlib.import_module(
            "apps.core.migrations.0012_minister_message_style_rewrite"
        )

    def test_the_new_message_has_no_em_dashes(self):
        self.assertNotIn("—", self.migration_module.NEW_FRENCH_MESSAGE)
        self.assertNotIn("—", self.migration_module.NEW_ENGLISH_MESSAGE)

    def test_the_new_message_drops_the_personal_biography(self):
        for phrase in ["Ingénieur de formation", "Secrétaire d'État", "juin 2025", "novembre 2025"]:
            self.assertNotIn(phrase, self.migration_module.NEW_FRENCH_MESSAGE)

    def test_the_new_message_covers_the_five_pillars_and_the_president(self):
        for phrase in ["orientation", "formation", "insertion", "emploi", "entrepreneuriat"]:
            self.assertIn(phrase, self.migration_module.NEW_FRENCH_MESSAGE)
        self.assertIn("Paul Biya", self.migration_module.NEW_FRENCH_MESSAGE)
        self.assertIn("Président de la République", self.migration_module.NEW_FRENCH_MESSAGE)

    def test_migration_overwrites_whatever_message_was_previously_stored(self):
        from django.apps import apps

        minister = MinisterMessage.load()
        minister.message_fr = "Un ancien message, quel qu'il soit."
        minister.message_en = "Some old message, whatever it was."
        minister.save()

        self.migration_module.rewrite_message(apps, None)

        minister.refresh_from_db()
        self.assertEqual(minister.message_fr, self.migration_module.NEW_FRENCH_MESSAGE)
        self.assertEqual(minister.message_en, self.migration_module.NEW_ENGLISH_MESSAGE)


class MinisterBiographyPageTests(TestCase):
    def setUp(self):
        self.minister = MinisterMessage.load()
        self.minister.full_name = "Mounouna Foutsou"
        self.minister.biography_fr = "Biographie de test.\n\n• Né en 1967."
        self.minister.biography_en = "Test biography.\n\n• Born in 1967."
        self.minister.save()

    def test_biography_page_renders_the_french_text_by_default(self):
        response = self.client.get(reverse("core:minister_biography"))
        self.assertContains(response, "Biographie de test.")

    def test_biography_page_renders_the_english_text_under_english_prefix(self):
        with translation.override("en"):
            response = self.client.get(reverse("core:minister_biography"))
        self.assertContains(response, "Test biography.")

    def test_biography_page_is_linked_from_the_minister_message_page(self):
        response = self.client.get(reverse("core:minister"))
        self.assertContains(response, reverse("core:minister_biography"))

    def test_minister_message_page_links_back_from_the_biography_page(self):
        response = self.client.get(reverse("core:minister_biography"))
        self.assertContains(response, reverse("core:minister"))


class SeedMinisterBiographyMigrationTests(TestCase):
    """The biography field is new — this migration backfills it (only when
    still blank, so it never overwrites an editor's own text) on an
    already-seeded database that predates the field."""

    def setUp(self):
        import importlib

        self.migration_module = importlib.import_module(
            "apps.core.migrations.0014_seed_minister_biography"
        )

    def test_the_biography_has_no_em_dashes(self):
        self.assertNotIn("—", self.migration_module.MINISTER_BIOGRAPHY_FR)
        self.assertNotIn("—", self.migration_module.MINISTER_BIOGRAPHY_EN)

    def test_the_biography_reflects_his_current_and_prior_roles(self):
        for phrase in [
            "27 juillet 2026",
            "Ministre de l'Emploi et de la Formation Professionnelle (par intérim)",
            "Ministre de la Jeunesse et de l'Éducation Civique",
        ]:
            self.assertIn(phrase, self.migration_module.MINISTER_BIOGRAPHY_FR)

    def test_migration_fills_in_a_blank_biography(self):
        from django.apps import apps

        minister = MinisterMessage.load()
        self.assertEqual(minister.biography_fr, "")

        self.migration_module.seed_biography(apps, None)

        minister.refresh_from_db()
        self.assertEqual(minister.biography_fr, self.migration_module.MINISTER_BIOGRAPHY_FR)
        self.assertEqual(minister.biography_en, self.migration_module.MINISTER_BIOGRAPHY_EN)

    def test_migration_does_not_overwrite_an_existing_biography(self):
        from django.apps import apps

        minister = MinisterMessage.load()
        minister.biography_fr = "Une biographie déjà rédigée par un éditeur."
        minister.save()

        self.migration_module.seed_biography(apps, None)

        minister.refresh_from_db()
        self.assertEqual(minister.biography_fr, "Une biographie déjà rédigée par un éditeur.")


class RetranslateStaleMinisterMessageMigrationTests(TestCase):
    """0009 only translated message_en for one exact known French string, so
    a database seeded with older wording (still mentioning the budget figures
    and youth-only phrasing since replaced) kept showing French on the
    English page. 0010's migration is meant to catch that any time
    message_en still equals message_fr and it's recognisably the ministry's
    standard message, regardless of exactly which historical wording it
    carries."""

    def setUp(self):
        import importlib

        self.minister = MinisterMessage.load()
        self.migration_module = importlib.import_module(
            "apps.core.migrations.0010_retranslate_stale_minister_message"
        )

    def test_a_stale_untranslated_message_with_older_wording_gets_fixed(self):
        older_french_wording = (
            "Chères concitoyennes, chers concitoyens,\n\n"
            "le Ministère a lancé le 19 novembre 2025 le programme « Un Jeune, un "
            "Métier, un Emploi » (JEME), doté d'une enveloppe de 17,72 milliards de "
            "FCFA, afin de former, insérer et autonomiser durablement les jeunes des "
            "zones rurales, péri-urbaines et urbaines."
        )
        self.minister.message_fr = older_french_wording
        self.minister.message_en = older_french_wording
        self.minister.save()

        self.migration_module.retranslate_if_stale(apps=self._real_apps(), schema_editor=None)

        self.minister.refresh_from_db()
        self.assertEqual(self.minister.message_fr, self.migration_module.CURRENT_FRENCH)
        self.assertEqual(self.minister.message_en, self.migration_module.CURRENT_ENGLISH)
        self.assertNotEqual(self.minister.message_en, self.minister.message_fr)

    def test_a_message_an_editor_has_already_customised_is_left_untouched(self):
        self.minister.message_fr = "Un message personnalisé sans rapport avec le JEME."
        self.minister.message_en = "Un message personnalisé sans rapport avec le JEME."
        self.minister.save()

        self.migration_module.retranslate_if_stale(apps=self._real_apps(), schema_editor=None)

        self.minister.refresh_from_db()
        self.assertEqual(self.minister.message_fr, "Un message personnalisé sans rapport avec le JEME.")

    @staticmethod
    def _real_apps():
        from django.apps import apps

        return apps
