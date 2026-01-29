def test_create_and_list(client):
    res = client.post("/api/pantry", json={"name": "Garlic", "quantity": 5, "unit": "cloves"})
    assert res.status_code == 201
    data = res.json()
    assert data["name"] == "garlic"
    assert data["quantity"] == 5

    res = client.get("/api/pantry")
    assert res.status_code == 200
    items = res.json()
    assert len(items) == 1


def test_get_single(client):
    res = client.post("/api/pantry", json={"name": "Olive Oil"})
    item_id = res.json()["id"]

    res = client.get(f"/api/pantry/{item_id}")
    assert res.status_code == 200
    assert res.json()["name"] == "olive oil"


def test_update(client):
    res = client.post("/api/pantry", json={"name": "Milk", "quantity": 1, "unit": "gallon"})
    item_id = res.json()["id"]

    res = client.put(f"/api/pantry/{item_id}", json={"quantity": 0.5})
    assert res.status_code == 200
    assert res.json()["quantity"] == 0.5
    assert res.json()["name"] == "milk"


def test_delete(client):
    res = client.post("/api/pantry", json={"name": "Butter"})
    item_id = res.json()["id"]

    res = client.delete(f"/api/pantry/{item_id}")
    assert res.status_code == 204

    res = client.get(f"/api/pantry/{item_id}")
    assert res.status_code == 404


def test_bulk_create(client):
    items = [
        {"name": "Salt"},
        {"name": "Pepper"},
        {"name": "Cumin"},
    ]
    res = client.post("/api/pantry/bulk", json=items)
    assert res.status_code == 201
    assert len(res.json()) == 3


def test_search(client):
    client.post("/api/pantry", json={"name": "chicken breast", "category": "meat"})
    client.post("/api/pantry", json={"name": "chicken thigh", "category": "meat"})
    client.post("/api/pantry", json={"name": "rice", "category": "grains"})

    res = client.get("/api/pantry?search=chicken")
    assert len(res.json()) == 2

    res = client.get("/api/pantry?category=meat")
    assert len(res.json()) == 2


def test_not_found(client):
    assert client.get("/api/pantry/999").status_code == 404
    assert client.put("/api/pantry/999", json={"name": "x"}).status_code == 404
    assert client.delete("/api/pantry/999").status_code == 404
