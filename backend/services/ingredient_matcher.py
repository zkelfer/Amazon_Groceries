"""Fuzzy matching of parsed ingredient names against pantry items using rapidfuzz."""

from dataclasses import dataclass

from rapidfuzz import fuzz, process


MATCH_THRESHOLD = 70  # minimum score to consider a match


@dataclass
class MatchResult:
    ingredient_name: str
    in_pantry: bool
    pantry_match: str | None = None
    score: float = 0.0


def match_ingredient(name: str, pantry_names: list[str]) -> MatchResult:
    """Match a single ingredient name against a list of pantry item names.

    Uses token_set_ratio which handles word reordering and partial matches well
    for ingredient names (e.g., "garlic cloves" vs "garlic").
    """
    if not name or not pantry_names:
        return MatchResult(ingredient_name=name, in_pantry=False)

    name_lower = name.lower().strip()

    # Exact match first
    for pn in pantry_names:
        if pn.lower().strip() == name_lower:
            return MatchResult(
                ingredient_name=name,
                in_pantry=True,
                pantry_match=pn,
                score=100.0,
            )

    # Fuzzy match
    result = process.extractOne(
        name_lower,
        [p.lower() for p in pantry_names],
        scorer=fuzz.token_set_ratio,
        score_cutoff=MATCH_THRESHOLD,
    )
    if result:
        match_text, score, idx = result
        return MatchResult(
            ingredient_name=name,
            in_pantry=True,
            pantry_match=pantry_names[idx],
            score=score,
        )

    return MatchResult(ingredient_name=name, in_pantry=False)


def match_many(
    ingredient_names: list[str], pantry_names: list[str]
) -> list[MatchResult]:
    """Match a list of ingredient names against pantry."""
    return [match_ingredient(name, pantry_names) for name in ingredient_names]
