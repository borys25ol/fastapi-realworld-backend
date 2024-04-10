from secrets import token_urlsafe

from slugify import slugify


def get_slug_from_title(title: str) -> str:
    slug = slugify(text=title, max_length=32, lowercase=True)
    unique_code = token_urlsafe(6)
    return f"{slug}-{unique_code.lower()}"
