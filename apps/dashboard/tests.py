from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse

from apps.blog.models import BlogPost
from apps.contact.models import ContactMessage
from apps.news.models import Article, NewsCategory

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
