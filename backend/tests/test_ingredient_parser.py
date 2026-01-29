from backend.services.ingredient_parser import parse_single, parse_many


def test_parse_single_basic():
    result = parse_single("2 cups flour")
    assert result.name  # should have parsed a name
    assert result.raw == "2 cups flour"


def test_parse_single_empty():
    result = parse_single("")
    assert result.name == ""


def test_parse_single_no_quantity():
    result = parse_single("salt")
    assert "salt" in result.name


def test_parse_many():
    results = parse_many(["1 cup milk", "2 eggs", "salt"])
    assert len(results) == 3
    for r in results:
        assert r.name
