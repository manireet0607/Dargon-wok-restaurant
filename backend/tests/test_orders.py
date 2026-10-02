from tests.conftest import API


def test_order_total_is_calculated_on_server(client, customer, order_payload):
    # 2 x 169 + 1 x 209 = 547.00 ; tax 5% = 27.35 ; delivery 40.00 ; total 614.35
    r = client.post(f"{API}/orders", json=order_payload, headers=customer["headers"])
    assert r.status_code == 201, r.text
    o = r.json()
    assert o["subtotal"] == "547.00" and o["tax_amount"] == "27.35" and o["delivery_fee"] == "40.00" and o["total_amount"] == "614.35"
    assert o["order_status"] == "pending" and o["payment_method"] == "cod" and o["payment_status"] == "pending"
    assert o["order_number"].startswith("DW-")
    assert {i["item_name"] for i in o["items"]} == {"Veg Hakka Noodles", "Chicken Hakka Noodles"}


def test_client_sent_prices_and_status_are_ignored(client, customer, order_payload):
    order_payload.update({"total_amount": "1.00", "order_status": "delivered", "payment_status": "paid", "delivery_fee": "0"})
    order_payload["items"][0]["unit_price"] = "1.00"
    r = client.post(f"{API}/orders", json=order_payload, headers=customer["headers"])
    assert r.status_code == 201
    assert r.json()["total_amount"] == "614.35" and r.json()["order_status"] == "pending" and r.json()["payment_status"] == "pending"


def test_order_numbers_are_unique(client, customer, order_payload):
    a = client.post(f"{API}/orders", json=order_payload, headers=customer["headers"]).json()
    b = client.post(f"{API}/orders", json=order_payload, headers=customer["headers"]).json()
    assert a["order_number"] != b["order_number"]


def test_duplicate_lines_are_merged(client, customer, order_payload):
    order_payload["items"] = [{"menu_item_id": 1, "quantity": 1}, {"menu_item_id": 1, "quantity": 2}]
    o = client.post(f"{API}/orders", json=order_payload, headers=customer["headers"]).json()
    assert len(o["items"]) == 1 and o["items"][0]["quantity"] == 3 and o["subtotal"] == "507.00"


def test_unit_price_is_saved_at_order_time(client, customer, admin, order_payload):
    oid = client.post(f"{API}/orders", json=order_payload, headers=customer["headers"]).json()["id"]
    item = client.get(f"{API}/menu/1").json()
    item.update({"price": "999.00"})
    body = {k: item[k] for k in ("category_id", "name", "description", "price", "image_url", "food_type", "is_available")}
    assert client.put(f"{API}/admin/menu/1", json=body, headers=admin["headers"]).status_code == 200
    old = client.get(f"{API}/orders/{oid}", headers=customer["headers"]).json()
    assert old["items"][0]["unit_price"] == "169.00" and old["total_amount"] == "614.35"


def test_invalid_orders(client, customer, order_payload):
    h = customer["headers"]
    def post(**changes):
        return client.post(f"{API}/orders", json={**order_payload, **changes}, headers=h)

    assert post(items=[]).status_code == 422
    assert post(items=[{"menu_item_id": 1, "quantity": 0}]).status_code == 422
    assert post(items=[{"menu_item_id": 1, "quantity": -2}]).status_code == 422
    assert post(items=[{"menu_item_id": 1, "quantity": 51}]).status_code == 422
    assert post(items=[{"menu_item_id": 999, "quantity": 1}]).status_code == 422  # unknown item
    assert post(items=[{"menu_item_id": 3, "quantity": 1}]).status_code == 409  # unavailable item
    assert post(customer_phone="abc").status_code == 422
    assert post(delivery_address="short").status_code == 422
    assert post(payment_method="card").status_code == 422
    assert post(customer_name="").status_code == 422


def test_order_requires_login(client, order_payload):
    assert client.post(f"{API}/orders", json=order_payload).status_code == 401


def test_customer_sees_only_own_orders(client, customer, order_payload):
    oid = client.post(f"{API}/orders", json=order_payload, headers=customer["headers"]).json()["id"]
    other = client.post(f"{API}/auth/register", json={"name": "Other", "email": "o@test.com", "phone": "9876500000", "password": "Secret123"}).json()
    oh = {"Authorization": f"Bearer {other['access_token']}"}
    assert client.get(f"{API}/orders", headers=oh).json() == []
    assert client.get(f"{API}/orders/{oid}", headers=oh).status_code == 404
    assert client.post(f"{API}/orders/{oid}/cancel", headers=oh).status_code == 404
    mine = client.get(f"{API}/orders", headers=customer["headers"]).json()
    assert len(mine) == 1 and mine[0]["id"] == oid


def test_customer_cannot_change_status(client, customer, order_payload):
    oid = client.post(f"{API}/orders", json=order_payload, headers=customer["headers"]).json()["id"]
    r = client.patch(f"{API}/admin/orders/{oid}/status", json={"status": "delivered"}, headers=customer["headers"])
    assert r.status_code == 403
    assert client.patch(f"{API}/orders/{oid}", json={"order_status": "delivered"}, headers=customer["headers"]).status_code in (404, 405)


def test_customer_can_cancel_pending_only(client, customer, admin, order_payload):
    oid = client.post(f"{API}/orders", json=order_payload, headers=customer["headers"]).json()["id"]
    assert client.post(f"{API}/orders/{oid}/cancel", headers=customer["headers"]).json()["order_status"] == "cancelled"
    oid2 = client.post(f"{API}/orders", json=order_payload, headers=customer["headers"]).json()["id"]
    client.patch(f"{API}/admin/orders/{oid2}/status", json={"status": "confirmed"}, headers=admin["headers"])
    assert client.post(f"{API}/orders/{oid2}/cancel", headers=customer["headers"]).status_code == 409
