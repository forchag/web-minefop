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


def directorate_list(request):
    directorates = OrgUnit.objects.filter(unit_type=OrgUnit.UnitType.DIRECTION).order_by("order")
    return render(request, "structures/directorate_list.html", {"directorates": directorates})


def directorate_detail(request, slug):
    directorate = get_object_or_404(OrgUnit, slug=slug, unit_type=OrgUnit.UnitType.DIRECTION)
    return render(request, "structures/directorate_detail.html", {"directorate": directorate})


def attached_bodies(request):
    """Bodies under the Ministry's supervision, then the programmes it steers."""
    context = {
        "bodies": AttachedBody.objects.filter(kind=AttachedBody.Kind.BODY),
        "programmes": AttachedBody.objects.filter(kind=AttachedBody.Kind.PROGRAMME),
    }
    return render(request, "structures/attached_bodies.html", context)


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
    ownership = request.GET.get("ownership")
    is_public = ownership != "private"
    centers = TrainingCenter.objects.filter(is_public=is_public).select_related("region")

    category = request.GET.get("category")
    if is_public and category:
        centers = centers.filter(category=category)

    region_id = request.GET.get("region")
    if is_public and region_id:
        centers = centers.filter(region_id=region_id)

    division = request.GET.get("division")
    if not is_public and division:
        centers = centers.filter(division=division)

    paginator = Paginator(centers, 12)
    page_obj = paginator.get_page(request.GET.get("page"))

    divisions = (
        Delegation.objects.filter(level=Delegation.Level.DEPARTMENTAL)
        .order_by("department_name")
        .values_list("department_name", flat=True)
        .distinct()
    )

    context = {
        "page_obj": page_obj,
        "regions": Region.objects.all(),
        "divisions": divisions,
        "categories": TrainingCenter.Category.choices,
        "ownership": "private" if not is_public else "public",
        "active_category": category,
        "active_region_id": int(region_id) if region_id else None,
        "active_division": division,
    }
    return render(request, "structures/training_centers.html", context)


def training_center_detail(request, pk):
    center = get_object_or_404(TrainingCenter, pk=pk)
    return render(request, "structures/training_center_detail.html", {"center": center})
