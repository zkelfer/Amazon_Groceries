def test_recipe_diff(client):
    # Add some pantry items
    client.post("/api/pantry", json={"name": "garlic"})
    client.post("/api/pantry", json={"name": "olive oil"})
    client.post("/api/pantry", json={"name": "salt"})

    res = client.post("/api/recipes/diff", json={
        "ingredients": ["3 cloves garlic", "2 tbsp olive oil", "1 lb chicken breast", "salt"],
        "recipe_title": "Simple Chicken",
        "recipe_url": "https://example.com/chicken",
    })
    assert res.status_code == 200
    data = res.json()
    assert data["recipe_title"] == "Simple Chicken"
    assert data["in_pantry_count"] >= 2  # garlic and olive oil at minimum
    assert data["missing_count"] >= 1   # chicken breast is missing

    # Check that missing items have Whole Foods URLs
    for ing in data["ingredients"]:
        if not ing["in_pantry"]:
            assert ing["whole_foods_url"] is not None
            assert "amazon.com" in ing["whole_foods_url"]


def test_recipe_parse(client):
    res = client.post("/api/recipes/parse", json={
        "ingredients": ["2 cups flour", "1 tsp salt", "3 eggs"],
    })
    assert res.status_code == 200
    data = res.json()
    assert len(data["parsed"]) == 3
    for p in data["parsed"]:
        assert p["name"]
        assert p["raw"]
