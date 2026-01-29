"""Wrap ingredient-parser-nlp to parse raw ingredient strings into structured data."""

from dataclasses import dataclass

try:
    from ingredient_parser import parse_ingredient
except ImportError:
    parse_ingredient = None


@dataclass
class ParsedIngredient:
    raw: str
    name: str
    quantity: float | None = None
    unit: str | None = None
    comment: str | None = None


def _try_float(val: str | None) -> float | None:
    if val is None:
        return None
    try:
        return float(val)
    except (ValueError, TypeError):
        # Handle fractions like "1/2"
        if "/" in str(val):
            parts = str(val).split("/")
            try:
                return float(parts[0]) / float(parts[1])
            except (ValueError, ZeroDivisionError):
                return None
        return None


def parse_single(raw: str) -> ParsedIngredient:
    """Parse a single raw ingredient string into structured data."""
    raw = raw.strip()
    if not raw:
        return ParsedIngredient(raw=raw, name="")

    if parse_ingredient is None:
        # Fallback: treat entire string as ingredient name
        return ParsedIngredient(raw=raw, name=raw.lower())

    result = parse_ingredient(raw)

    name = ""
    quantity = None
    unit = None
    comment = None

    if result.name:
        if isinstance(result.name, list):
            # List of IngredientText objects — join their text fields
            parts = []
            for part in result.name:
                parts.append(part.text.lower() if hasattr(part, "text") else str(part).lower())
            name = " ".join(parts)
        elif hasattr(result.name, "text"):
            name = result.name.text.lower()
        else:
            name = str(result.name).lower()

    if result.amount:
        amounts = result.amount if isinstance(result.amount, list) else [result.amount]
        if amounts:
            first = amounts[0]
            if hasattr(first, "quantity") and first.quantity:
                quantity = _try_float(first.quantity)
            if hasattr(first, "unit") and first.unit:
                unit = str(first.unit).lower()

    if result.comment:
        if isinstance(result.comment, list):
            parts = [c.text if hasattr(c, "text") else str(c) for c in result.comment]
            comment = " ".join(parts)
        elif hasattr(result.comment, "text"):
            comment = result.comment.text
        else:
            comment = str(result.comment)

    return ParsedIngredient(raw=raw, name=name or raw.lower(), quantity=quantity, unit=unit, comment=comment)


def parse_many(ingredients: list[str]) -> list[ParsedIngredient]:
    """Parse a list of raw ingredient strings."""
    return [parse_single(raw) for raw in ingredients]
