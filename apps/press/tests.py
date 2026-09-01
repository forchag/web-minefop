from datetime import date, datetime

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from apps.blog.models import BlogPost
from apps.core.choices import PressScope
from apps.news.models import Article

TINY_GIF = (
    b"GIF89a\x01\x00\x01\x00\x80\x00\x00\x00\x00\x00\xff\xff\xff!\xf9\x04"
    b"\x01\x00\x00\x00\x00,\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;"
)


def make_cover(name="cover.gif"):
    return SimpleUploadedFile(name, TINY_GIF, content_type="image/gif")


def make_datetime(year, month, day):
    return timezone.make_aware(datetime.combine(date(year, month, day), datetime.min.time()))


class PressListTests(TestCase):
    def setUp(self):
        self.national_article = Article.objects.create(
            title="Communiqué national",
            slug="communique-national",
            excerpt="Résumé national.",
            body="Contenu national.",
            scope=PressScope.NATIONAL,
            published_at=make_datetime(2026, 1, 10),
        )
        self.regional_post = BlogPost.objects.create(
            title_fr="Billet régional",
            title_en="Regional post",
            slug="billet-regional",
            author_name="Délégation du Centre",
            excerpt_fr="Résumé régional.",
            excerpt_en="Regional summary.",
            body_fr="Contenu régional.",
            body_en="Regional content.",
            cover_image=make_cover(),
            scope=PressScope.REGIONAL,
            published_at=make_datetime(2026, 1, 20),
        )
        self.draft_article = Article.objects.create(
            title="Brouillon",
            slug="brouillon-actualite",
            excerpt="Résumé.",
            body="Contenu.",
            is_published=False,
        )

    def test_list_shows_both_news_and_blog_items(self):
        response = self.client.get(reverse("press:list"))
        self.assertContains(response, self.national_article.title)
        self.assertContains(response, self.regional_post.title_fr)

    def test_list_hides_unpublished_items(self):
        response = self.client.get(reverse("press:list"))
        self.assertNotContains(response, self.draft_article.title)

    def test_list_is_sorted_by_date_descending_across_both_types(self):
        response = self.client.get(reverse("press:list"))
        page_obj = response.context["page_obj"]
        titles = [item.title if hasattr(item, "title") else item.title_fr for item in page_obj]
        self.assertEqual(titles[0], self.regional_post.title_fr)
        self.assertEqual(titles[1], self.national_article.title)

    def test_scope_filter_national(self):
        response = self.client.get(reverse("press:list"), {"portee": "national"})
        self.assertContains(response, self.national_article.title)
        self.assertNotContains(response, self.regional_post.title_fr)

    def test_scope_filter_regional(self):
        response = self.client.get(reverse("press:list"), {"portee": "regional"})
        self.assertContains(response, self.regional_post.title_fr)
        self.assertNotContains(response, self.national_article.title)


class PressDetailTests(TestCase):
    def setUp(self):
        self.article = Article.objects.create(
            title="Un communiqué",
            slug="un-communique",
            excerpt="Résumé du communiqué.",
            body="Corps du communiqué.",
        )
        self.post = BlogPost.objects.create(
            title_fr="Un billet",
            title_en="A post",
            slug="un-billet",
            author_name="Cellule de communication",
            excerpt_fr="Résumé du billet.",
            excerpt_en="Post summary.",
            body_fr="Corps du billet.",
            body_en="Post body.",
            cover_image=make_cover(),
        )

    def test_detail_resolves_news_article(self):
        response = self.client.get(reverse("press:detail", kwargs={"slug": self.article.slug}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.article.title)

    def test_detail_resolves_blog_post_with_author(self):
        response = self.client.get(reverse("press:detail", kwargs={"slug": self.post.slug}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.post.title_fr)
        self.assertContains(response, self.post.author_name)

    def test_detail_404s_for_unknown_slug(self):
        response = self.client.get(reverse("press:detail", kwargs={"slug": "inconnu"}))
        self.assertEqual(response.status_code, 404)

    def test_detail_404s_for_unpublished_article(self):
        self.article.is_published = False
        self.article.save(update_fields=["is_published"])
        response = self.client.get(reverse("press:detail", kwargs={"slug": self.article.slug}))
        self.assertEqual(response.status_code, 404)
