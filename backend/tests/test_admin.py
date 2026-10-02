from tests.conftest import API

NEW_ITEM = {"category_id": 1, "name": "Spring Rolls", "description": "Crisp rolls", "price": "149.00",
            "image_url": "/images/starters.svg", "food_type": "veg", "is_available": True}


def test_admin_menu_crud(client, admin):
    h = admin["headers"]
    r = client.post(f"{API}/admin/menu", json=NEW_ITEM, headers=h)
    assert r.status_code == 201 and r.json()["price"] == "149.00"
    iid = r.json()["id"]
    assert client.get(f"{API}/menu/{iid}").status_code == 200  # visible to customers

    r = client.put(f"{API}/admin/menu/{iid}", json={**NEW_ITEM, "price": "159.50", "name": "Veg Spring Rolls"}, headers=h)
    assert r.status_code == 200 and r.json()["price"] == "159.50" and r.json()["name"] == "Veg Spring Rolls"

    r = client.patch(f"{API}/admin/menu/{iid}/availability", json={"is_available": False}, headers=h)
    assert r.json()["is_available"] is False

    assert client.delete(f"{API}/admin/menu/{iid}", headers=h).status_code == 204
    assert client.get(f"{API}/menu/{iid}").status_code == 404


def test_admin_menu_validation(client, admin):
    h = admin["headers"]
    assert client.post(f"{API}/admin/menu", json={**NEW_ITEM, "price": "0"}, headers=h).status_code == 422
    assert client.post(f"{API}/admin/menu", json={**NEW_ITEM, "price": "-5"}, headers=h).status_code == 422
    assert client.post(f"{API}/admin/menu", json={**NEW_ITEM, "category_id": 999}, headers=h).status_code == 422
    assert client.post(f"{API}/admin/menu", json={**NEW_ITEM, "food_type": "vegan"}, headers=h).status_code == 422
    assert client.put(f"{API}/admin/menu/999", json=NEW_ITEM, headers=h).status_code == 404


def test_admin_menu_requires_admin(client, customer):
    assert client.post(f"{API}/admin/menu", json=NEW_ITEM, headers=customer["headers"]).status_code == 403
    assert client.post(f"{API}/admin/menu", json=NEW_ITEM).status_code == 401
    assert client.delete(f"{API}/admin/menu/1", headers=customer["headers"]).status_code == 403


def test_cannot_delete_item_used_in_orders(client, admin, customer, order_payload):
    client.post(f"{API}/orders", json=order_payload, headers=customer["headers"])
    r = client.delete(f"{API}/admin/menu/1", headers=admin["headers"])
    assert r.status_code == 409 and "availability" in r.json()["detail"]


def test_admin_category_crud(client, admin):
    h = admin["headers"]
    r = client.post(f"{API}/admin/categories", json={"name": "Momos", "description": "Dumplings"}, headers=h)
    assert r.status_code == 201
    cid = r.json()["id"]
    assert client.post(f"{API}/admin/categories", json={"name": "Momos"}, headers=h).status_code == 409
    assert client.put(f"{API}/admin/categories/{cid}", json={"name": "Dumplings"}, headers=h).json()["name"] == "Dumplings"
    assert client.delete(f"{API}/admin/categories/1", headers=h).status_code == 409  # has items
    assert client.delete(f"{API}/admin/categories/{cid}", headers=h).status_code == 204


def test_order_status_flow(client, admin, customer, order_payload):
    h = admin["headers"]
    oid = client.post(f"{API}/orders", json=order_payload, headers=customer["headers"]).json()["id"]

    def set_status(s):
        return client.patch(f"{API}/admin/orders/{oid}/status", json={"status": s}, headers=h)

    assert set_status("delivered").status_code == 409  # cannot skip steps
    assert set_status("preparing").status_code == 409
    for s in ("confirmed", "preparing", "out_for_delivery"):
        assert set_status(s).json()["order_status"] == s
    assert set_status("cancelled").status_code == 409  # too late to cancel
    done = set_status("delivered").json()
    assert done["order_status"] == "delivered" and done["payment_status"] == "paid"  # COD paid on delivery
    assert set_status("pending").status_code == 409  # finished orders are final
    assert client.patch(f"{API}/admin/orders/{oid}/status", json={"status": "nonsense"}, headers=h).status_code == 422
    assert client.patch(f"{API}/admin/orders/999/status", json={"status": "confirmed"}, headers=h).status_code == 404


def test_admin_can_cancel_before_delivery(client, admin, customer, order_payload):
    oid = client.post(f"{API}/orders", json=order_payload, headers=customer["headers"]).json()["id"]
    client.patch(f"{API}/admin/orders/{oid}/status", json={"status": "confirmed"}, headers=admin["headers"])
    r = client.patch(f"{API}/admin/orders/{oid}/status", json={"status": "cancelled"}, headers=admin["headers"])
    assert r.json()["order_status"] == "cancelled"


def test_admin_orders_stats_customers(client, admin, customer, order_payload):
    oid = client.post(f"{API}/orders", json=order_payload, headers=customer["headers"]).json()["id"]
    orders = client.get(f"{API}/admin/orders", headers=admin["headers"]).json()
    assert len(orders) == 1 and orders[0]["customer_email"] == "asha@test.com"
    assert client.get(f"{API}/admin/orders", params={"status": "delivered"}, headers=admin["headers"]).json() == []
    for s in ("confirmed", "preparing", "out_for_delivery", "delivered"):
        client.patch(f"{API}/admin/orders/{oid}/status", json={"status": s}, headers=admin["headers"])
    st = client.get(f"{API}/admin/stats", headers=admin["headers"]).json()
    assert st["total_orders"] == 1 and st["revenue"] == "614.35" and st["customers"] == 1 and st["menu_items"] == 3
    assert [c["email"] for c in client.get(f"{API}/admin/customers", headers=admin["headers"]).json()] == ["asha@test.com"]
