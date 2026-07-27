from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, render

from .models import Article, NewsCategory


def article_list(request):
    articles = Article.objects.filter(is_published=True).select_related("category")

    category_slug = request.GET.get("categorie")
    active_category = None
    if category_slug:
        active_category = get_object_or_404(NewsCategory, slug=category_slug)
        articles = articles.filter(category=active_category)

    paginator = Paginator(articles, 9)
    page_obj = paginator.get_page(request.GET.get("page"))

    context = {
        "page_obj": page_obj,
        "categories": NewsCategory.objects.all(),
        "active_category": active_category,
    }
    return render(request, "news/list.html", context)


def article_detail(request, slug):
    article = get_object_or_404(Article, slug=slug, is_published=True)
    related = (
        Article.objects.filter(is_published=True, category=article.category)
        .exclude(pk=article.pk)[:3]
    )
    return render(request, "news/detail.html", {"article": article, "related": related})
