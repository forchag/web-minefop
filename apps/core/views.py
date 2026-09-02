from django.core.paginator import Paginator
from django.db.models import F, Q
from django.http import HttpResponse
from django.shortcuts import render

from .models import HeroSlide, KeyFigure, MinisterMessage, PartnerSite, Timeline


def portal(request):
    """The entry page served at the root of the domain.

    It carries the State identification, the two language doors into the site
    and the directory of institutional, partner and online-service websites.
    """
    # Which tile sits on which side is an editorial decision, not a layout
    # one, so each entry carries its column and its rank within it.
    partners = PartnerSite.objects.filter(is_active=True)
    context = {
        "left_column": partners.filter(column=PartnerSite.Column.LEFT),
        "right_column": partners.filter(column=PartnerSite.Column.RIGHT),
    }
    return render(request, "core/portal.html", context)


def home(request):
    from itertools import chain

    from django.utils import timezone

    from apps.blog.models import BlogPost
    from apps.documents.models import Document
    from apps.media.models import Event
    from apps.news.models import Article

    articles = Article.objects.filter(is_published=True).select_related("category")
    posts = BlogPost.objects.filter(is_published=True)
    for article in articles:
        article.press_kind = "news"
    for post in posts:
        post.press_kind = "blog"
    latest_press = sorted(
        chain(articles, posts), key=lambda item: item.published_at, reverse=True
    )[:3]

    context = {
        "slides": HeroSlide.objects.filter(is_active=True),
        "key_figures": KeyFigure.objects.all(),
        "minister": MinisterMessage.objects.first(),
        "latest_press": latest_press,
        "latest_documents": Document.objects.order_by(
            F("published_date").desc(nulls_last=True), "title"
        )[:4],
        "upcoming_events": Event.objects.filter(
            is_published=True, start_at__gte=timezone.now()
        ).order_by("start_at")[:3],
    }
    return render(request, "core/home.html", context)


def mission(request):
    return render(request, "core/mission.html")


def history(request):
    context = {"timeline": Timeline.objects.all()}
    return render(request, "core/history.html", context)


def minister_message(request):
    context = {"minister": MinisterMessage.objects.first()}
    return render(request, "core/minister.html", context)


def vocational_training(request):
    """Presentation page: the national vocational-training framework (Loi 2018/010)."""
    return render(request, "core/vocational_training.html")


def search(request):
    """Site-wide search across press releases, official texts and training centres."""
    from apps.blog.models import BlogPost
    from apps.documents.models import Document
    from apps.news.models import Article
    from apps.structures.models import TrainingCenter

    query = (request.GET.get("q") or "").strip()
    results = []

    if query:
        for article in Article.objects.filter(is_published=True).filter(
            Q(title__icontains=query)
            | Q(excerpt__icontains=query)
            | Q(body__icontains=query)
        )[:40]:
            results.append(
                {
                    "kind": "news",
                    "title": article.title,
                    "summary": article.excerpt,
                    "url": article.get_absolute_url(),
                    "date": article.published_at,
                }
            )

        for post in BlogPost.objects.filter(is_published=True).filter(
            Q(title_fr__icontains=query)
            | Q(title_en__icontains=query)
            | Q(excerpt_fr__icontains=query)
            | Q(excerpt_en__icontains=query)
            | Q(body_fr__icontains=query)
            | Q(body_en__icontains=query)
        )[:40]:
            results.append(
                {
                    "kind": "news",
                    "title": post.title,
                    "summary": post.excerpt,
                    "url": post.get_absolute_url(),
                    "date": post.published_at,
                }
            )

        for document in Document.objects.filter(
            Q(title__icontains=query)
            | Q(reference_number__icontains=query)
            | Q(description__icontains=query)
        )[:40]:
            results.append(
                {
                    "kind": "document",
                    "title": document.title,
                    "summary": document.reference_number or document.description,
                    "url": document.download_url,
                    "date": document.published_date,
                }
            )

        for center in TrainingCenter.objects.select_related("region").filter(
            Q(name__icontains=query)
            | Q(town__icontains=query)
            | Q(specialties__icontains=query)
        )[:40]:
            results.append(
                {
                    "kind": "center",
                    "title": center.name,
                    "summary": f"{center.get_center_type_display()} — {center.town}",
                    "url": center.get_absolute_url(),
                    "date": None,
                }
            )

    paginator = Paginator(results, 15)
    context = {
        "query": query,
        "page_obj": paginator.get_page(request.GET.get("page")),
        "result_count": len(results),
    }
    return render(request, "core/search.html", context)


def legal_notice(request):
    return render(request, "core/legal_notice.html")


def accessibility(request):
    return render(request, "core/accessibility.html")


def sitemap_page(request):
    """Human-readable site map (the machine-readable one lives at /sitemap.xml)."""
    from apps.documents.models import DocumentCategory

    context = {
        "document_categories": DocumentCategory.objects.all(),
    }
    return render(request, "core/sitemap.html", context)


def robots_txt(request):
    host = request.get_host()
    lines = [
        "User-agent: *",
        "Disallow: /admin/",
        "Allow: /",
        "",
        f"Sitemap: {request.scheme}://{host}/sitemap.xml",
    ]
    return HttpResponse("\n".join(lines), content_type="text/plain; charset=utf-8")


def error_404(request, exception=None):
    return render(request, "errors/404.html", status=404)


def error_500(request):
    return render(request, "errors/500.html", status=500)
