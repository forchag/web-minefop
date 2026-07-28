from django.shortcuts import render

from .models import HeroSlide, KeyFigure, MinisterMessage, Timeline


def home(request):
    from apps.news.models import Article
    from apps.documents.models import Document

    context = {
        "slides": HeroSlide.objects.filter(is_active=True),
        "key_figures": KeyFigure.objects.all(),
        "minister": MinisterMessage.objects.first(),
        "latest_articles": Article.objects.filter(is_published=True).order_by(
            "-published_at"
        )[:3],
        "latest_documents": Document.objects.order_by("-published_date")[:4],
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


def error_403(request, exception=None):
    return render(request, "errors/403.html", {"exception": str(exception) if exception else ""}, status=403)


def error_404(request, exception=None):
    return render(request, "errors/404.html", status=404)


def error_500(request):
    return render(request, "errors/500.html", status=500)
