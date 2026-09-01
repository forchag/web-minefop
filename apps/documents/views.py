from django.core.paginator import Paginator
from django.db.models import F
from django.shortcuts import render

from .models import Document, DocumentCategory


def document_list(request):
    # Dated official texts come first; the undated documentary holdings follow,
    # grouped by collection (category, then the reference label naming the set).
    documents = Document.objects.select_related("category").order_by(
        F("published_date").desc(nulls_last=True),
        "category__order",
        "reference_number",
        "title",
    )

    category_slug = request.GET.get("categorie")
    active_category = None
    if category_slug:
        # An unrecognised slug (a stale link, a typo) falls back to showing
        # every document rather than erroring — the category filter is a
        # refinement, not a hard requirement for the page to work.
        active_category = DocumentCategory.objects.filter(slug=category_slug).first()
        if active_category:
            documents = documents.filter(category=active_category)

    paginator = Paginator(documents, 12)
    page_obj = paginator.get_page(request.GET.get("page"))

    context = {
        "page_obj": page_obj,
        "categories": DocumentCategory.objects.all(),
        "active_category": active_category,
    }
    return render(request, "documents/list.html", context)
