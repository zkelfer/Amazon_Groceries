"""Generate Whole Foods search URLs for missing ingredients."""

from urllib.parse import quote_plus

WHOLE_FOODS_SEARCH = "https://www.amazon.com/s?k={query}&i=wholefoods"


def whole_foods_url(ingredient_name: str) -> str:
    """Build an Amazon Whole Foods search URL for the given ingredient."""
    return WHOLE_FOODS_SEARCH.format(query=quote_plus(ingredient_name.strip()))
