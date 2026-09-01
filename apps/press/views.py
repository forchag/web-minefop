from itertools import chain

from django.core.paginator import Paginator
from django.http import Http404
from django.shortcuts import render

from apps.blog.models import BlogPost
from apps.core.choices import PressScope
from apps.news.models import Article

PAGE_SIZE = 9


def _tag(items, kind):
    for item in items:
        item.press_kind = kind
    return items


def press_list(request):
    """Merged "Communiqués de presse" list: news articles and blog posts,
    interleaved by publication date, optionally filtered by scope."""
    scope = request.GET.get("portee")

    articles = Article.objects.filter(is_published=True).select_related("category")
    posts = BlogPost.objects.filter(is_published=True)
    if scope in PressScope.values:
        articles = articles.filter(scope=scope)
        posts = posts.filter(scope=scope)

    combined = sorted(
        chain(_tag(articles, "news"), _tag(posts, "blog")),
        key=lambda item: item.published_at,
        reverse=True,
    )

    paginator = Paginator(combined, PAGE_SIZE)
    page_obj = paginator.get_page(request.GET.get("page"))
    return render(request, "press/list.html", {"page_obj": page_obj, "active_scope": scope})


def press_detail(request, slug):
    """One URL space for both content types: try a news article, then a
    blog post, and render whichever matches."""
    article = Article.objects.filter(slug=slug, is_published=True).select_related("category").first()
    if article is not None:
        article.press_kind = "news"
        related = _tag(
            list(
                Article.objects.filter(is_published=True)
                .exclude(pk=article.pk)
                .order_by("-published_at")[:3]
            ),
            "news",
        )
        return render(request, "press/detail.html", {"item": article, "related": related})

    post = BlogPost.objects.filter(slug=slug, is_published=True).prefetch_related("attachments").first()
    if post is not None:
        post.press_kind = "blog"
        related = _tag(
            list(
                BlogPost.objects.filter(is_published=True)
                .exclude(pk=post.pk)
                .order_by("-published_at")[:3]
            ),
            "blog",
        )
        return render(request, "press/detail.html", {"item": post, "related": related})

    raise Http404
