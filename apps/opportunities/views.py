from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, render

from .models import Opportunity


def opportunity_list(request):
    opportunities = Opportunity.objects.filter(is_published=True)

    kind = request.GET.get("type")
    if kind in Opportunity.Kind.values:
        opportunities = opportunities.filter(kind=kind)

    paginator = Paginator(opportunities, 9)
    page_obj = paginator.get_page(request.GET.get("page"))
    return render(request, "opportunities/list.html", {"page_obj": page_obj, "active_kind": kind})


def opportunity_detail(request, slug):
    opportunity = get_object_or_404(Opportunity, slug=slug, is_published=True)
    related = Opportunity.objects.filter(is_published=True).exclude(pk=opportunity.pk)[:3]
    return render(
        request, "opportunities/detail.html", {"opportunity": opportunity, "related": related}
    )
