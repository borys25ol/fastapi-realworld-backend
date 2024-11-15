from secrets import token_urlsafe

from slugify import slugify


def make_slug_from_title(title: str) -> str:
    """
    Create a unique slug from the title.

    Example:
        make_slug_from_title("Hello World")
        "hello-world-123456"
    """
    slug = slugify(text=title, max_length=32, lowercase=True)
    unique_code = token_urlsafe(6)
    return f"{slug}-{unique_code.lower()}"


def make_slug_from_title_and_code(title: str, code: str) -> str:
    """
    Create a unique slug from the title and code.

    Example:
        make_slug_from_title_and_code("Hello World", "123456")
        "hello-world-123456"
    """
    slug = slugify(text=title, max_length=32, lowercase=True)
    return f"{slug}-{code}"


def get_slug_unique_part(slug: str) -> str:
    """
    Get unique part of the slug.

    Example:
        get_slug_unique_part("hello-world-123456")
        "123456"
    """
    return slug.split("-")[-1]
