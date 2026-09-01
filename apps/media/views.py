from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, render

from .models import Event, GalleryPhoto


def event_list(request):
    events = Event.objects.filter(is_published=True)
    paginator = Paginator(events, 9)
    page_obj = paginator.get_page(request.GET.get("page"))
    return render(request, "media/event_list.html", {"page_obj": page_obj})


def event_detail(request, slug):
    event = get_object_or_404(Event, slug=slug, is_published=True)
    photos = event.photos.filter(is_published=True)
    return render(request, "media/event_detail.html", {"event": event, "photos": photos})


def gallery_list(request):
    photos = GalleryPhoto.objects.filter(is_published=True).select_related("event")

    event_id = request.GET.get("evenement")
    if event_id:
        photos = photos.filter(event_id=event_id)

    paginator = Paginator(photos, 24)
    page_obj = paginator.get_page(request.GET.get("page"))
    context = {
        "page_obj": page_obj,
        "events": Event.objects.filter(is_published=True),
        "active_event_id": int(event_id) if event_id else None,
    }
    return render(request, "media/gallery_list.html", context)
