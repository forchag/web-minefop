from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from django.utils import translation

from .models import MAX_ATTACHMENTS_PER_POST, BlogAttachment, BlogPost

# A 1x1 transparent GIF, valid enough for FileField storage in tests.
TINY_GIF = (
    b"GIF89a\x01\x00\x01\x00\x80\x00\x00\x00\x00\x00\xff\xff\xff!\xf9\x04"
    b"\x01\x00\x00\x00\x00,\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;"
)


def make_cover(name="cover.gif"):
    return SimpleUploadedFile(name, TINY_GIF, content_type="image/gif")


class BlogPostModelTests(TestCase):
    def setUp(self):
        self.published = BlogPost.objects.create(
            title_fr="Un article publié",
            title_en="A published article",
            slug="un-article-publie",
            author_name="Cellule de communication",
            excerpt_fr="Un court résumé de l'article.",
            excerpt_en="A short summary of the article.",
            body_fr="Le contenu détaillé de l'article.",
            body_en="The detailed content of the article.",
            cover_image=make_cover(),
        )

    def test_title_follows_active_language(self):
        self.assertEqual(self.published.title, self.published.title_fr)
        with translation.override("en"):
            self.assertEqual(self.published.title, self.published.title_en)
            self.assertEqual(self.published.excerpt, self.published.excerpt_en)
            self.assertEqual(self.published.body, self.published.body_en)

    def test_get_absolute_url_points_at_the_merged_press_section(self):
        self.assertEqual(self.published.get_absolute_url(), f"/fr/presse/{self.published.slug}/")


class OldBlogUrlsRedirectToPressTests(TestCase):
    """Blog posts are now shown through apps.press; the old /blog/ routes
    must keep working as permanent redirects for bookmarked/indexed links."""

    def setUp(self):
        self.post = BlogPost.objects.create(
            title_fr="Un article publié",
            title_en="A published article",
            slug="un-article-publie",
            author_name="Cellule de communication",
            excerpt_fr="Résumé.",
            excerpt_en="Summary.",
            body_fr="Contenu.",
            body_en="Content.",
            cover_image=make_cover(),
        )

    def test_old_list_url_redirects_permanently_to_press(self):
        response = self.client.get(reverse("blog:list"))
        self.assertRedirects(
            response, reverse("press:list"), status_code=301, fetch_redirect_response=False
        )

    def test_old_detail_url_redirects_permanently_to_press(self):
        response = self.client.get(reverse("blog:detail", kwargs={"slug": self.post.slug}))
        self.assertRedirects(
            response,
            reverse("press:detail", kwargs={"slug": self.post.slug}),
            status_code=301,
            fetch_redirect_response=False,
        )


class BlogAttachmentModelTests(TestCase):
    def setUp(self):
        self.post = BlogPost.objects.create(
            title_fr="Article avec pièces jointes",
            title_en="Article with attachments",
            slug="article-pieces-jointes",
            author_name="Direction de la communication",
            excerpt_fr="Résumé.",
            excerpt_en="Summary.",
            body_fr="Contenu.",
            body_en="Content.",
            cover_image=make_cover(),
        )

    def test_display_title_falls_back_to_filename(self):
        attachment = BlogAttachment.objects.create(
            post=self.post,
            file=SimpleUploadedFile("note-de-service.pdf", b"%PDF-1.4 fake"),
        )
        self.assertIn("note-de-service", attachment.display_title)

    def test_display_title_uses_explicit_title(self):
        attachment = BlogAttachment.objects.create(
            post=self.post,
            file=SimpleUploadedFile("note-de-service.pdf", b"%PDF-1.4 fake"),
            title="Note de service n°12",
        )
        self.assertEqual(attachment.display_title, "Note de service n°12")

    def test_extension_property(self):
        attachment = BlogAttachment.objects.create(
            post=self.post,
            file=SimpleUploadedFile("brochure.PNG", b"fake"),
        )
        self.assertEqual(attachment.extension, "png")

    def test_up_to_ten_attachments_allowed(self):
        for index in range(MAX_ATTACHMENTS_PER_POST):
            BlogAttachment.objects.create(
                post=self.post,
                file=SimpleUploadedFile(f"doc-{index}.pdf", b"%PDF-1.4 fake"),
            )
        self.assertEqual(self.post.attachments.count(), MAX_ATTACHMENTS_PER_POST)
