from tests.conftest import API, auth_header


def test_register_returns_token_and_customer_role(client):
    r = client.post(f"{API}/auth/register", json={"name": "Ravi", "email": "Ravi@Test.com", "phone": "+91 98765 43210", "password": "Secret123"})
    assert r.status_code == 201
    body = r.json()
    assert body["user"]["role"] == "customer"
    assert body["user"]["email"] == "ravi@test.com"  # stored in lower case
    assert body["user"]["phone"] == "+919876543210"
    assert "password" not in str(body)


def test_register_cannot_choose_admin_role(client):
    r = client.post(f"{API}/auth/register", json={"name": "Evil", "email": "evil@test.com", "phone": "9876543210", "password": "Secret123", "role": "admin"})
    assert r.status_code == 201
    assert r.json()["user"]["role"] == "customer"


def test_register_duplicate_email(client, customer):
    r = client.post(f"{API}/auth/register", json={"name": "Asha 2", "email": "asha@test.com", "phone": "9876543210", "password": "Secret123"})
    assert r.status_code == 409


def test_register_validation(client):
    bad = {"name": "A", "email": "not-an-email", "phone": "12", "password": "short"}
    r = client.post(f"{API}/auth/register", json=bad)
    assert r.status_code == 422
    r = client.post(f"{API}/auth/register", json={"name": "Ravi", "email": "r@test.com", "phone": "9876543210", "password": "onlyletters"})
    assert r.status_code == 422  # needs a number


def test_password_is_hashed(client, db_session, customer):
    from app.models import User
    u = db_session.query(User).filter_by(email="asha@test.com").one()
    assert u.password_hash != "Secret123" and u.password_hash.startswith("$2")


def test_login_success_and_failure(client, customer):
    ok = client.post(f"{API}/auth/login", json={"email": "asha@test.com", "password": "Secret123"})
    assert ok.status_code == 200 and ok.json()["access_token"]
    assert client.post(f"{API}/auth/login", json={"email": "asha@test.com", "password": "wrongpass1"}).status_code == 401
    assert client.post(f"{API}/auth/login", json={"email": "nobody@test.com", "password": "Secret123"}).status_code == 401


def test_profile_requires_token(client, customer):
    assert client.get(f"{API}/users/me").status_code == 401
    assert client.get(f"{API}/users/me", headers=auth_header("garbage")).status_code == 401
    r = client.get(f"{API}/users/me", headers=customer["headers"])
    assert r.status_code == 200 and r.json()["email"] == "asha@test.com"


def test_expired_token_rejected(client, customer, monkeypatch):
    from app.core import security
    monkeypatch.setattr(security.get_settings(), "access_token_expire_minutes", -1)
    token = security.create_access_token(customer["user"]["id"], "customer")
    assert client.get(f"{API}/users/me", headers=auth_header(token)).status_code == 401


def test_customer_cannot_use_admin_api(client, customer, admin):
    for method, path in [("get", "/admin/stats"), ("get", "/admin/orders"), ("get", "/admin/menu"), ("get", "/admin/customers")]:
        assert getattr(client, method)(f"{API}{path}", headers=customer["headers"]).status_code == 403
        assert getattr(client, method)(f"{API}{path}").status_code == 401
        assert getattr(client, method)(f"{API}{path}", headers=admin["headers"]).status_code == 200
