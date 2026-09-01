from django.utils.text import slugify


def unique_slug(model, base_text, *, instance=None, max_length=270):
    """Generate a unique slug for `model` from `base_text`, so the dashboard
    forms never have to ask an editor to type or fix one by hand."""
    base = slugify(base_text)[:max_length] or "article"
    slug = base
    queryset = model.objects.all()
    if instance is not None and instance.pk:
        queryset = queryset.exclude(pk=instance.pk)
    suffix = 2
    while queryset.filter(slug=slug).exists():
        candidate = f"{base}-{suffix}"
        slug = candidate[:max_length]
        suffix += 1
    return slug
