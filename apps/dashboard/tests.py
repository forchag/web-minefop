from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse

from apps.blog.models import BlogPost
from apps.contact.models import ContactMessage
from apps.documents.models import Document, DocumentCategory
from apps.media.models import Event, GalleryPhoto
from apps.news.models import Article, NewsCategory
from apps.opportunities.models import Opportunity
from apps.structures.models import OrgUnit

TINY_GIF = (
    b"GIF89a\x01\x00\x01\x00\x80\x00\x00\x00\x00\x00\xff\xff\xff!\xf9\x04"
    b"\x01\x00\x00\x00\x00,\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;"
)


def make_image(name="cover.gif"):
    return SimpleUploadedFile(name, TINY_GIF, content_type="image/gif")


class DashboardAccessTests(TestCase):
    def setUp(self):
        self.staff_user = get_user_model().objects.create_user(
            username="agent", password="s3cret-pass!", is_staff=True
        )
        self.regular_user = get_user_model().objects.create_user(
            username="visiteur", password="s3cret-pass!", is_staff=False
        )

    def test_anonymous_user_is_redirected_to_login(self):
        response = self.client.get(reverse("dashboard:home"))
        self.assertRedirects(response, f"{reverse('dashboard:login')}?next={reverse('dashboard:home')}")

    def test_non_staff_user_cannot_log_in_to_dashboard(self):
        response = self.client.post(
            reverse("dashboard:login"),
            {"username": "visiteur", "password": "s3cret-pass!"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "non autorisé")
        self.assertFalse(response.wsgi_request.user.is_authenticated)

    def test_staff_user_can_log_in_and_reach_home(self):
        response = self.client.post(
            reverse("dashboard:login"),
            {"username": "agent", "password": "s3cret-pass!"},
            follow=True,
        )
        self.assertRedirects(response, reverse("dashboard:home"))
        self.assertContains(response, "Bienvenue")

    def test_dashboard_chrome_stays_french_regardless_of_browser_language(self):
        self.client.force_login(self.staff_user)
        response = self.client.get(reverse("dashboard:blog_list"), HTTP_ACCEPT_LANGUAGE="en-US,en;q=0.9")
        self.assertContains(response, "Articles de blog")
        self.assertNotContains(response, "Blog posts")

    def test_logout_requires_post(self):
        self.client.force_login(self.staff_user)
        response = self.client.get(reverse("dashboard:logout"))
        self.assertEqual(response.status_code, 405)


class DashboardBlogCrudTests(TestCase):
    def setUp(self):
        self.staff_user = get_user_model().objects.create_user(
            username="agent", password="s3cret-pass!", is_staff=True
        )
        self.client.force_login(self.staff_user)

    def _post_data(self, **overrides):
        data = {
            "title_fr": "Titre en français",
            "title_en": "Title in English",
            "author_name": "Cellule de communication",
            "excerpt_fr": "Résumé en français.",
            "excerpt_en": "Summary in English.",
            "body_fr": "Contenu en français.",
            "body_en": "Content in English.",
            "is_published": "on",
            "published_at": "2026-01-01T10:00",
            "attachments-TOTAL_FORMS": "0",
            "attachments-INITIAL_FORMS": "0",
            "attachments-MIN_NUM_FORMS": "0",
            "attachments-MAX_NUM_FORMS": "10",
        }
        data.update(overrides)
        return data

    def test_create_blog_post_in_one_submit(self):
        response = self.client.post(
            reverse("dashboard:blog_create"),
            {**self._post_data(), "cover_image": make_image()},
        )
        self.assertRedirects(response, reverse("dashboard:blog_list"))
        post = BlogPost.objects.get(title_fr="Titre en français")
        self.assertEqual(post.title_en, "Title in English")
        self.assertTrue(post.slug)
        self.assertEqual(post.created_by, self.staff_user)

    def test_slug_is_generated_automatically(self):
        self.client.post(reverse("dashboard:blog_create"), {**self._post_data(), "cover_image": make_image()})
        post = BlogPost.objects.get(title_fr="Titre en français")
        self.assertEqual(post.slug, "titre-en-francais")

    def test_edit_existing_post(self):
        post = BlogPost.objects.create(
            title_fr="Ancien titre",
            title_en="Old title",
            slug="ancien-titre",
            author_name="Cellule",
            excerpt_fr="Ancien résumé.",
            excerpt_en="Old summary.",
            body_fr="Ancien contenu.",
            body_en="Old content.",
            cover_image=make_image(),
        )
        response = self.client.post(
            reverse("dashboard:blog_edit", args=[post.pk]),
            self._post_data(title_fr="Nouveau titre"),
        )
        self.assertRedirects(response, reverse("dashboard:blog_list"))
        post.refresh_from_db()
        self.assertEqual(post.title_fr, "Nouveau titre")
        self.assertEqual(post.slug, "ancien-titre")

    def test_toggle_publish_flips_status_in_one_click(self):
        post = BlogPost.objects.create(
            title_fr="Article",
            title_en="Article",
            slug="article",
            author_name="Cellule",
            excerpt_fr="Résumé.",
            excerpt_en="Summary.",
            body_fr="Contenu.",
            body_en="Content.",
            cover_image=make_image(),
            is_published=True,
        )
        self.client.post(reverse("dashboard:blog_toggle_publish", args=[post.pk]))
        post.refresh_from_db()
        self.assertFalse(post.is_published)

    def test_delete_requires_confirmation_page_then_post(self):
        post = BlogPost.objects.create(
            title_fr="À supprimer",
            title_en="To delete",
            slug="a-supprimer",
            author_name="Cellule",
            excerpt_fr="Résumé.",
            excerpt_en="Summary.",
            body_fr="Contenu.",
            body_en="Content.",
            cover_image=make_image(),
        )
        confirm_response = self.client.get(reverse("dashboard:blog_delete", args=[post.pk]))
        self.assertEqual(confirm_response.status_code, 200)
        self.assertTrue(BlogPost.objects.filter(pk=post.pk).exists())

        delete_response = self.client.post(reverse("dashboard:blog_delete", args=[post.pk]))
        self.assertRedirects(delete_response, reverse("dashboard:blog_list"))
        self.assertFalse(BlogPost.objects.filter(pk=post.pk).exists())


class DashboardNewsCrudTests(TestCase):
    def setUp(self):
        self.staff_user = get_user_model().objects.create_user(
            username="agent", password="s3cret-pass!", is_staff=True
        )
        self.client.force_login(self.staff_user)
        self.category = NewsCategory.objects.create(name="Communiqué", slug="communique")

    def test_create_article_in_one_submit(self):
        response = self.client.post(
            reverse("dashboard:news_create"),
            {
                "title": "Une actualité",
                "category": self.category.pk,
                "excerpt": "Résumé.",
                "body": "Contenu détaillé.",
                "is_published": "on",
                "published_at": "2026-01-01T10:00",
            },
        )
        self.assertRedirects(response, reverse("dashboard:news_list"))
        article = Article.objects.get(title="Une actualité")
        self.assertEqual(article.slug, "une-actualite")

    def test_toggle_publish(self):
        article = Article.objects.create(
            title="Actualité", slug="actualite", excerpt="R.", body="C.", is_published=True
        )
        self.client.post(reverse("dashboard:news_toggle_publish", args=[article.pk]))
        article.refresh_from_db()
        self.assertFalse(article.is_published)


class DashboardMessageInboxTests(TestCase):
    def setUp(self):
        self.staff_user = get_user_model().objects.create_user(
            username="agent", password="s3cret-pass!", is_staff=True
        )
        self.client.force_login(self.staff_user)
        self.message = ContactMessage.objects.create(
            name="Jean Usager",
            email="jean@example.cm",
            subject="Question sur un centre de formation",
            message="Bonjour, ...",
        )

    def test_message_list_shows_unread_badge(self):
        response = self.client.get(reverse("dashboard:message_list"))
        self.assertContains(response, "Non lu")

    def test_opening_message_marks_it_read(self):
        self.assertFalse(self.message.is_read)
        response = self.client.get(reverse("dashboard:message_detail", args=[self.message.pk]))
        self.assertEqual(response.status_code, 200)
        self.message.refresh_from_db()
        self.assertTrue(self.message.is_read)


class DashboardOpportunityCrudTests(TestCase):
    def setUp(self):
        self.staff_user = get_user_model().objects.create_user(
            username="agent", password="s3cret-pass!", is_staff=True
        )
        self.client.force_login(self.staff_user)

    def test_create_opportunity_in_one_submit(self):
        response = self.client.post(
            reverse("dashboard:opportunity_create"),
            {
                "title": "Concours d'entrée au CNFFDP",
                "kind": "concours",
                "organisme": "CNFFDP",
                "summary": "Résumé.",
                "description": "Description détaillée.",
                "conditions": "",
                "application_url": "",
                "contact_email": "",
                "is_published": "on",
                "published_at": "2026-01-01T10:00",
            },
        )
        self.assertRedirects(response, reverse("dashboard:opportunity_list"))
        opportunity = Opportunity.objects.get(title="Concours d'entrée au CNFFDP")
        self.assertEqual(opportunity.slug, "concours-dentree-au-cnffdp")

    def test_toggle_publish(self):
        opportunity = Opportunity.objects.create(
            title="Offre", slug="offre", organisme="MINEFOP", summary="R.", description="D.",
        )
        self.client.post(reverse("dashboard:opportunity_toggle_publish", args=[opportunity.pk]))
        opportunity.refresh_from_db()
        self.assertFalse(opportunity.is_published)

    def test_delete_requires_confirmation_then_post(self):
        opportunity = Opportunity.objects.create(
            title="À supprimer", slug="a-supprimer", organisme="MINEFOP", summary="R.", description="D.",
        )
        confirm = self.client.get(reverse("dashboard:opportunity_delete", args=[opportunity.pk]))
        self.assertEqual(confirm.status_code, 200)
        self.client.post(reverse("dashboard:opportunity_delete", args=[opportunity.pk]))
        self.assertFalse(Opportunity.objects.filter(pk=opportunity.pk).exists())


class DashboardDocumentCrudTests(TestCase):
    def setUp(self):
        self.staff_user = get_user_model().objects.create_user(
            username="agent", password="s3cret-pass!", is_staff=True
        )
        self.client.force_login(self.staff_user)
        self.category = DocumentCategory.objects.create(name="Lois", slug="lois")

    def test_create_document_in_one_submit(self):
        response = self.client.post(
            reverse("dashboard:document_create"),
            {
                "title": "Loi n° 2018/010",
                "category": self.category.pk,
                "reference_number": "Loi n° 2018/010",
                "description": "",
                "source_url": "",
                "published_date": "2018-07-11",
            },
        )
        self.assertRedirects(response, reverse("dashboard:document_list"))
        self.assertTrue(Document.objects.filter(title="Loi n° 2018/010").exists())

    def test_delete_document(self):
        document = Document.objects.create(title="À supprimer")
        self.client.post(reverse("dashboard:document_delete", args=[document.pk]))
        self.assertFalse(Document.objects.filter(pk=document.pk).exists())


class DashboardEventCrudTests(TestCase):
    def setUp(self):
        self.staff_user = get_user_model().objects.create_user(
            username="agent", password="s3cret-pass!", is_staff=True
        )
        self.client.force_login(self.staff_user)

    def test_create_event_in_one_submit(self):
        response = self.client.post(
            reverse("dashboard:event_create"),
            {
                "title": "Forum de l'emploi",
                "description": "Description.",
                "location": "Yaoundé",
                "start_at": "2026-03-01T09:00",
                "end_at": "",
                "is_published": "on",
            },
        )
        self.assertRedirects(response, reverse("dashboard:event_list"))
        event = Event.objects.get(title="Forum de l'emploi")
        self.assertEqual(event.slug, "forum-de-lemploi")

    def test_toggle_publish(self):
        event = Event.objects.create(title="Événement", slug="evenement", description="D.")
        self.client.post(reverse("dashboard:event_toggle_publish", args=[event.pk]))
        event.refresh_from_db()
        self.assertFalse(event.is_published)


class DashboardPhotoCrudTests(TestCase):
    def setUp(self):
        self.staff_user = get_user_model().objects.create_user(
            username="agent", password="s3cret-pass!", is_staff=True
        )
        self.client.force_login(self.staff_user)

    def test_create_photo_in_one_submit(self):
        response = self.client.post(
            reverse("dashboard:photo_create"),
            {"title": "Photo test", "image": make_image(), "order": 0, "is_published": "on"},
        )
        self.assertRedirects(response, reverse("dashboard:photo_list"))
        self.assertTrue(GalleryPhoto.objects.filter(title="Photo test").exists())

    def test_delete_photo(self):
        photo = GalleryPhoto.objects.create(title="À supprimer", image=make_image())
        self.client.post(reverse("dashboard:photo_delete", args=[photo.pk]))
        self.assertFalse(GalleryPhoto.objects.filter(pk=photo.pk).exists())


class DashboardDirectorateEditTests(TestCase):
    def setUp(self):
        self.staff_user = get_user_model().objects.create_user(
            username="agent", password="s3cret-pass!", is_staff=True
        )
        self.client.force_login(self.staff_user)
        self.directorate = OrgUnit.objects.create(
            name="Direction des Affaires Générales",
            unit_type=OrgUnit.UnitType.DIRECTION,
            head_title="Directeur",
        )

    def test_directorate_gets_a_slug_on_save(self):
        self.assertEqual(self.directorate.slug, "direction-des-affaires-generales")

    def test_list_shows_directorate(self):
        response = self.client.get(reverse("dashboard:directorate_list"))
        self.assertContains(response, self.directorate.name)

    def test_edit_updates_mission_and_contact_only(self):
        response = self.client.post(
            reverse("dashboard:directorate_edit", args=[self.directorate.pk]),
            {
                "mission": "Nouvelle mission.",
                "director_name": "M. Jean Dupont",
                "director_email": "jean.dupont@minefop.gov.cm",
            },
        )
        self.assertRedirects(response, reverse("dashboard:directorate_list"))
        self.directorate.refresh_from_db()
        self.assertEqual(self.directorate.mission, "Nouvelle mission.")
        self.assertEqual(self.directorate.director_name, "M. Jean Dupont")
        self.assertEqual(self.directorate.name, "Direction des Affaires Générales")

    def test_create_a_new_directorate(self):
        response = self.client.post(
            reverse("dashboard:directorate_create"),
            {
                "name": "Direction du Numérique",
                "head_title": "Directeur",
                "legal_reference": "",
                "mission": "Numérisation des services du Ministère.",
                "director_name": "",
                "director_email": "",
                "order": 20,
            },
        )
        created = OrgUnit.objects.get(name="Direction du Numérique")
        self.assertRedirects(response, reverse("dashboard:directorate_edit", args=[created.pk]))
        self.assertEqual(created.unit_type, OrgUnit.UnitType.DIRECTION)
        self.assertTrue(created.slug)

    def test_add_and_edit_a_sous_direction(self):
        create_response = self.client.post(
            reverse("dashboard:sous_direction_create", args=[self.directorate.pk]),
            {
                "name": "Sous-direction des Systèmes d'Information",
                "head_title": "Sous-directeur",
                "legal_reference": "",
                "mission": "Exploitation des systèmes d'information du Ministère.",
                "director_name": "",
                "director_email": "",
                "order": 1,
            },
        )
        self.assertRedirects(create_response, reverse("dashboard:directorate_edit", args=[self.directorate.pk]))
        sous_direction = OrgUnit.objects.get(name="Sous-direction des Systèmes d'Information")
        self.assertEqual(sous_direction.unit_type, OrgUnit.UnitType.SOUS_DIRECTION)
        self.assertEqual(sous_direction.parent, self.directorate)

        edit_response = self.client.post(
            reverse("dashboard:sous_direction_edit", args=[sous_direction.pk]),
            {
                "mission": "Mission mise à jour.",
                "director_name": "Mme Ada",
                "director_email": "ada@minefop.gov.cm",
            },
        )
        self.assertRedirects(edit_response, reverse("dashboard:directorate_edit", args=[self.directorate.pk]))
        sous_direction.refresh_from_db()
        self.assertEqual(sous_direction.mission, "Mission mise à jour.")
        self.assertEqual(sous_direction.director_name, "Mme Ada")

    def test_directorate_edit_page_lists_its_sous_directions(self):
        OrgUnit.objects.create(
            name="Sous-direction du Budget",
            unit_type=OrgUnit.UnitType.SOUS_DIRECTION,
            parent=self.directorate,
        )
        response = self.client.get(reverse("dashboard:directorate_edit", args=[self.directorate.pk]))
        self.assertContains(response, "Sous-direction du Budget")


class DashboardLanguageSwitchTests(TestCase):
    def setUp(self):
        self.staff_user = get_user_model().objects.create_user(
            username="agent", password="s3cret-pass!", is_staff=True
        )
        self.client.force_login(self.staff_user)

    def test_switching_to_english_via_the_dashboard_switcher_sticks(self):
        self.client.post(
            reverse("set_language"),
            {"language": "en", "next": reverse("dashboard:blog_list")},
        )
        response = self.client.get(reverse("dashboard:blog_list"))
        self.assertContains(response, "Blog articles")
