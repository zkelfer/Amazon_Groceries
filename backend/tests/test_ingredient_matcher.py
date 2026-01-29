from backend.services.ingredient_matcher import match_ingredient, match_many


def test_exact_match():
    result = match_ingredient("garlic", ["garlic", "onion", "salt"])
    assert result.in_pantry is True
    assert result.pantry_match == "garlic"
    assert result.score == 100.0


def test_fuzzy_match():
    result = match_ingredient("garlic cloves", ["garlic", "onion", "salt"])
    assert result.in_pantry is True
    assert result.pantry_match == "garlic"
    assert result.score >= 70


def test_no_match():
    result = match_ingredient("saffron", ["garlic", "onion", "salt"])
    assert result.in_pantry is False
    assert result.pantry_match is None


def test_empty_pantry():
    result = match_ingredient("garlic", [])
    assert result.in_pantry is False


def test_empty_name():
    result = match_ingredient("", ["garlic"])
    assert result.in_pantry is False


def test_match_many():
    pantry = ["garlic", "olive oil", "salt", "pepper"]
    results = match_many(["garlic", "cumin", "salt"], pantry)
    assert results[0].in_pantry is True
    assert results[1].in_pantry is False
    assert results[2].in_pantry is True
