from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, render

from .models import AttachedBody, Delegation, OrgUnit, Region, TrainingCenter


def org_chart(request):
    top_level = (
        OrgUnit.objects.filter(parent__isnull=True)
        .prefetch_related("children__children__children")
    )
    context = {"top_level": top_level}
    return render(request, "structures/org_chart.html", context)


def attached_bodies(request):
    return render(request, "structures/attached_bodies.html", {"bodies": AttachedBody.objects.all()})


def delegations(request):
    region_id = request.GET.get("region")
    qs = Delegation.objects.select_related("region")
    if region_id:
        qs = qs.filter(region_id=region_id)
    context = {
        "regions": Region.objects.all(),
        "delegations": qs,
        "active_region_id": int(region_id) if region_id else None,
    }
    return render(request, "structures/delegations.html", context)


def training_center_list(request):
    centers = TrainingCenter.objects.select_related("region")

    center_type = request.GET.get("type")
    if center_type:
        centers = centers.filter(center_type=center_type)

    region_id = request.GET.get("region")
    if region_id:
        centers = centers.filter(region_id=region_id)

    paginator = Paginator(centers, 12)
    page_obj = paginator.get_page(request.GET.get("page"))

    context = {
        "page_obj": page_obj,
        "regions": Region.objects.all(),
        "center_types": TrainingCenter.CenterType.choices,
        "active_type": center_type,
        "active_region_id": int(region_id) if region_id else None,
    }
    return render(request, "structures/training_centers.html", context)


def training_center_detail(request, pk):
    center = get_object_or_404(TrainingCenter, pk=pk)
    return render(request, "structures/training_center_detail.html", {"center": center})
