from datetime import timedelta

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from django.utils.html import escape

from .models import Event, GalleryPhoto

TINY_GIF = (
    b"GIF89a\x01\x00\x01\x00\x80\x00\x00\x00\x00\x00\xff\xff\xff!\xf9\x04"
    b"\x01\x00\x00\x00\x00,\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;"
)


def make_image(name="photo.gif"):
    return SimpleUploadedFile(name, TINY_GIF, content_type="image/gif")


class EventTests(TestCase):
    def setUp(self):
        self.upcoming = Event.objects.create(
            title="Lancement d'un centre de formation",
            slug="lancement-centre-formation",
            description="Cérémonie de lancement.",
            location="Yaoundé",
            start_at=timezone.now() + timedelta(days=10),
        )
        self.draft = Event.objects.create(
            title="Événement brouillon",
            slug="evenement-brouillon",
            description="Description.",
            start_at=timezone.now(),
            is_published=False,
        )

    def test_list_shows_only_published(self):
        response = self.client.get(reverse("media:event_list"))
        self.assertContains(response, escape(self.upcoming.title))
        self.assertNotContains(response, escape(self.draft.title))

    def test_is_upcoming_property(self):
        self.assertTrue(self.upcoming.is_upcoming)

    def test_detail_shows_published_event(self):
        response = self.client.get(reverse("media:event_detail", kwargs={"slug": self.upcoming.slug}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, escape(self.upcoming.title))

    def test_detail_404s_for_unpublished(self):
        response = self.client.get(reverse("media:event_detail", kwargs={"slug": self.draft.slug}))
        self.assertEqual(response.status_code, 404)


class GalleryTests(TestCase):
    def setUp(self):
        self.event = Event.objects.create(
            title="Forum de l'emploi",
            slug="forum-emploi",
            description="Description.",
            start_at=timezone.now(),
        )
        self.photo = GalleryPhoto.objects.create(
            title="Ouverture du forum",
            image=make_image(),
            event=self.event,
        )
        self.unpublished_photo = GalleryPhoto.objects.create(
            title="Photo non publiée",
            image=make_image("unpub.gif"),
            is_published=False,
        )

    def test_gallery_shows_only_published_photos(self):
        response = self.client.get(reverse("media:gallery_list"))
        self.assertContains(response, escape(self.photo.title))
        self.assertNotContains(response, escape(self.unpublished_photo.title))

    def test_gallery_filters_by_event(self):
        other_photo = GalleryPhoto.objects.create(title="Autre photo", image=make_image("other.gif"))
        response = self.client.get(reverse("media:gallery_list"), {"evenement": self.event.pk})
        self.assertContains(response, escape(self.photo.title))
        self.assertNotContains(response, escape(other_photo.title))
