from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, render

from .models import Document, DocumentCategory


def document_list(request):
    documents = Document.objects.select_related("category")

    category_slug = request.GET.get("categorie")
    active_category = None
    if category_slug:
        active_category = get_object_or_404(DocumentCategory, slug=category_slug)
        documents = documents.filter(category=active_category)

    paginator = Paginator(documents, 12)
    page_obj = paginator.get_page(request.GET.get("page"))

    context = {
        "page_obj": page_obj,
        "categories": DocumentCategory.objects.all(),
        "active_category": active_category,
    }
    return render(request, "documents/list.html", context)
