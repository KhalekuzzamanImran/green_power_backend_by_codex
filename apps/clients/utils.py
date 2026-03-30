from django.utils.text import slugify


def normalize_client_code(raw_value):
    normalized = slugify((raw_value or "").strip()).replace("-", "_").upper().strip("_")
    return normalized or "CLIENT"


def generate_unique_client_code(site_name, *, model, exclude_client_id=None):
    base_code = normalize_client_code(site_name)
    candidate = base_code
    suffix = 2

    existing_codes = model.objects.all()
    if exclude_client_id:
        existing_codes = existing_codes.exclude(pk=exclude_client_id)

    while existing_codes.filter(code=candidate).exists():
        candidate = f"{base_code}_{suffix}"
        suffix += 1

    return candidate
