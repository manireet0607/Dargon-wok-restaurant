from tests.conftest import API


def test_categories(client):
    r = client.get(f"{API}/categories")
    assert r.status_code == 200
    assert [c["name"] for c in r.json()] == ["Noodles", "Soups"]


def test_menu_list_has_expected_fields(client):
    r = client.get(f"{API}/menu")
    assert r.status_code == 200
    items = r.json()
    assert len(items) == 3
    veg = next(i for i in items if i["name"] == "Veg Hakka Noodles")
    assert veg["price"] == "169.00" and veg["food_type"] == "veg" and veg["category_name"] == "Noodles"
    assert veg["is_available"] is True
    assert next(i for i in items if i["name"] == "Hot and Sour Soup")["is_available"] is False


def test_menu_filters(client):
    assert len(client.get(f"{API}/menu", params={"category_id": 1}).json()) == 2
    assert [i["name"] for i in client.get(f"{API}/menu", params={"food_type": "non_veg"}).json()] == ["Chicken Hakka Noodles"]
    assert len(client.get(f"{API}/menu", params={"search": "soup"}).json()) == 1
    assert client.get(f"{API}/menu", params={"food_type": "bad"}).status_code == 422


def test_menu_item_detail_and_404(client):
    assert client.get(f"{API}/menu/1").json()["name"] == "Veg Hakka Noodles"
    assert client.get(f"{API}/menu/999").status_code == 404


def test_public_config(client):
    r = client.get(f"{API}/config")
    assert r.json()["delivery_fee"] == "40.00" and r.json()["currency"] == "INR"


def test_health(client):
    assert client.get("/health").json() == {"status": "ok"}
    assert client.get("/health/ready").status_code in (200, 503)
