from django.contrib import messages
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.core.paginator import Paginator
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.translation import gettext as _
from django.views.decorators.http import require_POST

from apps.blog.models import BlogPost
from apps.contact.models import ContactMessage
from apps.documents.models import Document
from apps.media.models import Event, GalleryPhoto
from apps.news.models import Article
from apps.opportunities.models import Opportunity
from apps.structures.models import OrgUnit

from .decorators import staff_required
from .forms import (
    ArticleForm,
    BlogAttachmentFormSet,
    BlogPostForm,
    DashboardLoginForm,
    DirectorateForm,
    DocumentForm,
    EventForm,
    GalleryPhotoForm,
    OpportunityForm,
)
from .utils import unique_slug

LIST_PAGE_SIZE = 20


def dashboard_login(request):
    if request.user.is_authenticated and request.user.is_staff:
        return redirect("dashboard:home")

    if request.method == "POST":
        form = DashboardLoginForm(request, data=request.POST)
        if form.is_valid():
            auth_login(request, form.get_user())
            next_url = request.POST.get("next") or request.GET.get("next") or reverse("dashboard:home")
            return redirect(next_url)
    else:
        form = DashboardLoginForm(request)

    return render(request, "dashboard/login.html", {"form": form})


@require_POST
def dashboard_logout(request):
    auth_logout(request)
    return redirect("dashboard:login")


@staff_required
def dashboard_home(request):
    context = {
        "blog_total": BlogPost.objects.count(),
        "blog_published": BlogPost.objects.filter(is_published=True).count(),
        "article_total": Article.objects.count(),
        "article_published": Article.objects.filter(is_published=True).count(),
        "opportunity_total": Opportunity.objects.count(),
        "opportunity_published": Opportunity.objects.filter(is_published=True).count(),
        "event_total": Event.objects.count(),
        "event_published": Event.objects.filter(is_published=True).count(),
        "document_total": Document.objects.count(),
        "photo_total": GalleryPhoto.objects.count(),
        "unread_messages": ContactMessage.objects.filter(is_read=False).count(),
        "recent_posts": BlogPost.objects.order_by("-created_at")[:5],
        "recent_messages": ContactMessage.objects.order_by("-created_at")[:5],
    }
    return render(request, "dashboard/home.html", context)


# ---------------------------------------------------------------------------
# Blog posts
# ---------------------------------------------------------------------------

@staff_required
def blog_list(request):
    paginator = Paginator(BlogPost.objects.order_by("-published_at"), LIST_PAGE_SIZE)
    page_obj = paginator.get_page(request.GET.get("page"))
    return render(request, "dashboard/blog_list.html", {"page_obj": page_obj})


@staff_required
def blog_form_view(request, pk=None):
    post = get_object_or_404(BlogPost, pk=pk) if pk else None
    is_new = post is None

    if request.method == "POST":
        form = BlogPostForm(request.POST, request.FILES, instance=post)
        formset = BlogAttachmentFormSet(request.POST, request.FILES, instance=post)
        if form.is_valid() and formset.is_valid():
            with transaction.atomic():
                obj = form.save(commit=False)
                if not obj.slug:
                    obj.slug = unique_slug(BlogPost, obj.title_fr, instance=obj)
                if is_new:
                    obj.created_by = request.user
                obj.save()
                formset.instance = obj
                formset.save()
            messages.success(
                request,
                _("Article « %(title)s » enregistré.") % {"title": obj.title_fr},
            )
            return redirect("dashboard:blog_list")
    else:
        form = BlogPostForm(instance=post)
        formset = BlogAttachmentFormSet(instance=post)

    return render(
        request,
        "dashboard/blog_form.html",
        {"form": form, "formset": formset, "post": post, "is_new": is_new},
    )


@staff_required
@require_POST
def blog_toggle_publish(request, pk):
    post = get_object_or_404(BlogPost, pk=pk)
    post.is_published = not post.is_published
    post.save(update_fields=["is_published"])
    return redirect("dashboard:blog_list")


@staff_required
def blog_delete(request, pk):
    post = get_object_or_404(BlogPost, pk=pk)
    if request.method == "POST":
        title = post.title_fr
        post.delete()
        messages.success(request, _("Article « %(title)s » supprimé.") % {"title": title})
        return redirect("dashboard:blog_list")
    return render(request, "dashboard/blog_confirm_delete.html", {"post": post})


# ---------------------------------------------------------------------------
# News articles
# ---------------------------------------------------------------------------

@staff_required
def news_list(request):
    paginator = Paginator(Article.objects.order_by("-published_at"), LIST_PAGE_SIZE)
    page_obj = paginator.get_page(request.GET.get("page"))
    return render(request, "dashboard/news_list.html", {"page_obj": page_obj})


@staff_required
def news_form_view(request, pk=None):
    article = get_object_or_404(Article, pk=pk) if pk else None
    is_new = article is None

    if request.method == "POST":
        form = ArticleForm(request.POST, request.FILES, instance=article)
        if form.is_valid():
            obj = form.save(commit=False)
            if not obj.slug:
                obj.slug = unique_slug(Article, obj.title, instance=obj)
            obj.save()
            messages.success(
                request,
                _("Actualité « %(title)s » enregistrée.") % {"title": obj.title},
            )
            return redirect("dashboard:news_list")
    else:
        form = ArticleForm(instance=article)

    return render(
        request,
        "dashboard/news_form.html",
        {"form": form, "article": article, "is_new": is_new},
    )


@staff_required
@require_POST
def news_toggle_publish(request, pk):
    article = get_object_or_404(Article, pk=pk)
    article.is_published = not article.is_published
    article.save(update_fields=["is_published"])
    return redirect("dashboard:news_list")


@staff_required
def news_delete(request, pk):
    article = get_object_or_404(Article, pk=pk)
    if request.method == "POST":
        title = article.title
        article.delete()
        messages.success(request, _("Actualité « %(title)s » supprimée.") % {"title": title})
        return redirect("dashboard:news_list")
    return render(request, "dashboard/news_confirm_delete.html", {"article": article})


# ---------------------------------------------------------------------------
# Contact messages inbox
# ---------------------------------------------------------------------------

@staff_required
def message_list(request):
    paginator = Paginator(ContactMessage.objects.order_by("-created_at"), LIST_PAGE_SIZE)
    page_obj = paginator.get_page(request.GET.get("page"))
    return render(request, "dashboard/message_list.html", {"page_obj": page_obj})


@staff_required
def message_detail(request, pk):
    message_obj = get_object_or_404(ContactMessage, pk=pk)
    if not message_obj.is_read:
        message_obj.is_read = True
        message_obj.save(update_fields=["is_read"])
    return render(request, "dashboard/message_detail.html", {"message_obj": message_obj})


# ---------------------------------------------------------------------------
# Opportunities & concours
# ---------------------------------------------------------------------------

@staff_required
def opportunity_list(request):
    paginator = Paginator(Opportunity.objects.order_by("-published_at"), LIST_PAGE_SIZE)
    page_obj = paginator.get_page(request.GET.get("page"))
    return render(request, "dashboard/opportunity_list.html", {"page_obj": page_obj})


@staff_required
def opportunity_form_view(request, pk=None):
    opportunity = get_object_or_404(Opportunity, pk=pk) if pk else None
    is_new = opportunity is None

    if request.method == "POST":
        form = OpportunityForm(request.POST, request.FILES, instance=opportunity)
        if form.is_valid():
            obj = form.save(commit=False)
            if not obj.slug:
                obj.slug = unique_slug(Opportunity, obj.title, instance=obj)
            obj.save()
            messages.success(
                request, _("Opportunité « %(title)s » enregistrée.") % {"title": obj.title}
            )
            return redirect("dashboard:opportunity_list")
    else:
        form = OpportunityForm(instance=opportunity)

    return render(
        request,
        "dashboard/opportunity_form.html",
        {"form": form, "opportunity": opportunity, "is_new": is_new},
    )


@staff_required
@require_POST
def opportunity_toggle_publish(request, pk):
    opportunity = get_object_or_404(Opportunity, pk=pk)
    opportunity.is_published = not opportunity.is_published
    opportunity.save(update_fields=["is_published"])
    return redirect("dashboard:opportunity_list")


@staff_required
def opportunity_delete(request, pk):
    opportunity = get_object_or_404(Opportunity, pk=pk)
    if request.method == "POST":
        title = opportunity.title
        opportunity.delete()
        messages.success(request, _("Opportunité « %(title)s » supprimée.") % {"title": title})
        return redirect("dashboard:opportunity_list")
    return render(request, "dashboard/opportunity_confirm_delete.html", {"opportunity": opportunity})


# ---------------------------------------------------------------------------
# Documents
# ---------------------------------------------------------------------------

@staff_required
def document_list(request):
    paginator = Paginator(
        Document.objects.select_related("category").order_by("-published_date", "title"),
        LIST_PAGE_SIZE,
    )
    page_obj = paginator.get_page(request.GET.get("page"))
    return render(request, "dashboard/document_list.html", {"page_obj": page_obj})


@staff_required
def document_form_view(request, pk=None):
    document = get_object_or_404(Document, pk=pk) if pk else None
    is_new = document is None

    if request.method == "POST":
        form = DocumentForm(request.POST, request.FILES, instance=document)
        if form.is_valid():
            obj = form.save()
            messages.success(request, _("Document « %(title)s » enregistré.") % {"title": obj.title})
            return redirect("dashboard:document_list")
    else:
        form = DocumentForm(instance=document)

    return render(
        request,
        "dashboard/document_form.html",
        {"form": form, "document": document, "is_new": is_new},
    )


@staff_required
def document_delete(request, pk):
    document = get_object_or_404(Document, pk=pk)
    if request.method == "POST":
        title = document.title
        document.delete()
        messages.success(request, _("Document « %(title)s » supprimé.") % {"title": title})
        return redirect("dashboard:document_list")
    return render(request, "dashboard/document_confirm_delete.html", {"document": document})


# ---------------------------------------------------------------------------
# Events
# ---------------------------------------------------------------------------

@staff_required
def event_list(request):
    paginator = Paginator(Event.objects.order_by("-start_at"), LIST_PAGE_SIZE)
    page_obj = paginator.get_page(request.GET.get("page"))
    return render(request, "dashboard/event_list.html", {"page_obj": page_obj})


@staff_required
def event_form_view(request, pk=None):
    event = get_object_or_404(Event, pk=pk) if pk else None
    is_new = event is None

    if request.method == "POST":
        form = EventForm(request.POST, request.FILES, instance=event)
        if form.is_valid():
            obj = form.save(commit=False)
            if not obj.slug:
                obj.slug = unique_slug(Event, obj.title, instance=obj)
            obj.save()
            messages.success(request, _("Événement « %(title)s » enregistré.") % {"title": obj.title})
            return redirect("dashboard:event_list")
    else:
        form = EventForm(instance=event)

    return render(
        request, "dashboard/event_form.html", {"form": form, "event": event, "is_new": is_new}
    )


@staff_required
@require_POST
def event_toggle_publish(request, pk):
    event = get_object_or_404(Event, pk=pk)
    event.is_published = not event.is_published
    event.save(update_fields=["is_published"])
    return redirect("dashboard:event_list")


@staff_required
def event_delete(request, pk):
    event = get_object_or_404(Event, pk=pk)
    if request.method == "POST":
        title = event.title
        event.delete()
        messages.success(request, _("Événement « %(title)s » supprimé.") % {"title": title})
        return redirect("dashboard:event_list")
    return render(request, "dashboard/event_confirm_delete.html", {"event": event})


# ---------------------------------------------------------------------------
# Photo gallery
# ---------------------------------------------------------------------------

@staff_required
def photo_list(request):
    paginator = Paginator(
        GalleryPhoto.objects.select_related("event").order_by("order", "-uploaded_at"),
        LIST_PAGE_SIZE,
    )
    page_obj = paginator.get_page(request.GET.get("page"))
    return render(request, "dashboard/photo_list.html", {"page_obj": page_obj})


@staff_required
def photo_form_view(request, pk=None):
    photo = get_object_or_404(GalleryPhoto, pk=pk) if pk else None
    is_new = photo is None

    if request.method == "POST":
        form = GalleryPhotoForm(request.POST, request.FILES, instance=photo)
        if form.is_valid():
            obj = form.save()
            messages.success(request, _("Photo enregistrée."))
            return redirect("dashboard:photo_list")
    else:
        form = GalleryPhotoForm(instance=photo)

    return render(
        request, "dashboard/photo_form.html", {"form": form, "photo": photo, "is_new": is_new}
    )


@staff_required
def photo_delete(request, pk):
    photo = get_object_or_404(GalleryPhoto, pk=pk)
    if request.method == "POST":
        photo.delete()
        messages.success(request, _("Photo supprimée."))
        return redirect("dashboard:photo_list")
    return render(request, "dashboard/photo_confirm_delete.html", {"photo": photo})


# ---------------------------------------------------------------------------
# Directorates (mission text & responsible contact only — the org chart
# structure itself is fixed by decree and stays out of the dashboard).
# ---------------------------------------------------------------------------

@staff_required
def directorate_list(request):
    directorates = OrgUnit.objects.filter(unit_type=OrgUnit.UnitType.DIRECTION).order_by("order")
    return render(request, "dashboard/directorate_list.html", {"directorates": directorates})


@staff_required
def directorate_edit(request, pk):
    directorate = get_object_or_404(OrgUnit, pk=pk, unit_type=OrgUnit.UnitType.DIRECTION)

    if request.method == "POST":
        form = DirectorateForm(request.POST, instance=directorate)
        if form.is_valid():
            form.save()
            messages.success(
                request, _("Direction « %(name)s » mise à jour.") % {"name": directorate.name}
            )
            return redirect("dashboard:directorate_list")
    else:
        form = DirectorateForm(instance=directorate)

    return render(
        request, "dashboard/directorate_form.html", {"form": form, "directorate": directorate}
    )
