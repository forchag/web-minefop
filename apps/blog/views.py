from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, render

from .models import BlogPost


def post_list(request):
    posts = BlogPost.objects.filter(is_published=True)
    paginator = Paginator(posts, 9)
    page_obj = paginator.get_page(request.GET.get("page"))
    return render(request, "blog/list.html", {"page_obj": page_obj})


def post_detail(request, slug):
    post = get_object_or_404(
        BlogPost.objects.prefetch_related("attachments"), slug=slug, is_published=True
    )
    related = BlogPost.objects.filter(is_published=True).exclude(pk=post.pk)[:3]
    return render(request, "blog/detail.html", {"post": post, "related": related})
