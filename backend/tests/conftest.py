import os

os.environ["ENVIRONMENT"] = "test"
os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["SECRET_KEY"] = "test-secret-key-test-secret-key-1234"
os.environ["DELIVERY_FEE"] = "40.00"
os.environ["TAX_RATE"] = "0.05"
os.environ["FREE_DELIVERY_ABOVE"] = "0"

from decimal import Decimal  # noqa: E402

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy import create_engine  # noqa: E402
from sqlalchemy.orm import sessionmaker  # noqa: E402
from sqlalchemy.pool import StaticPool  # noqa: E402

from app.core.security import hash_password  # noqa: E402
from app.db.base import Base  # noqa: E402
from app.db.session import get_db  # noqa: E402
from app.main import app  # noqa: E402
from app.models import Category, MenuItem, User  # noqa: E402

API = "/api/v1"


@pytest.fixture()
def db_session():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    session = Session()
    noodles = Category(name="Noodles", description="Noodles")
    soups = Category(name="Soups", description="Soups")
    session.add_all([noodles, soups])
    session.flush()
    session.add_all([
        MenuItem(category_id=noodles.id, name="Veg Hakka Noodles", description="d", price=Decimal("169.00"), food_type="veg"),
        MenuItem(category_id=noodles.id, name="Chicken Hakka Noodles", description="d", price=Decimal("209.00"), food_type="non_veg"),
        MenuItem(category_id=soups.id, name="Hot and Sour Soup", description="d", price=Decimal("129.00"), food_type="veg", is_available=False),
    ])
    session.add(User(name="Admin", email="admin@test.com", phone="9999999999", password_hash=hash_password("Admin12345"), role="admin"))
    session.commit()
    yield session
    session.close()
    engine.dispose()


@pytest.fixture()
def client(db_session):
    def override():
        yield db_session

    app.dependency_overrides[get_db] = override
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


def auth_header(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture()
def customer(client):
    r = client.post(f"{API}/auth/register", json={"name": "Asha Rao", "email": "asha@test.com", "phone": "9876543210", "password": "Secret123"})
    assert r.status_code == 201, r.text
    return {"token": r.json()["access_token"], "headers": auth_header(r.json()["access_token"]), "user": r.json()["user"]}


@pytest.fixture()
def admin(client):
    r = client.post(f"{API}/auth/login", json={"email": "admin@test.com", "password": "Admin12345"})
    assert r.status_code == 200, r.text
    return {"headers": auth_header(r.json()["access_token"])}


@pytest.fixture()
def order_payload():
    return {
        "items": [{"menu_item_id": 1, "quantity": 2}, {"menu_item_id": 2, "quantity": 1}],
        "customer_name": "Asha Rao",
        "customer_phone": "9876543210",
        "delivery_address": "12 Palm Street, Dwarka, New Delhi 110075",
        "special_instructions": "Less spicy",
        "payment_method": "cod",
    }
