"""Seed sample data. Safe to run many times (it only adds what is missing).

Usage:  python -m app.db.seed
"""
import logging
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.security import hash_password
from app.db.session import SessionLocal
from app.models import Category, MenuItem, User

log = logging.getLogger("dragonwok.seed")

CATEGORIES = [
    ("Chinese Starters", "Crispy, saucy bites to begin your meal", "starters"),
    ("Noodles", "Wok-tossed noodles with smoky wok hei", "noodles"),
    ("Fried Rice", "Fragrant rice fried on high heat", "rice"),
    ("Chinese Main Course", "Rich gravies and dry specials", "main"),
    ("Soups", "Hot bowls, made fresh every day", "soups"),
    ("Momos", "Hand-folded dumplings, steamed or fried", "momos"),
    ("Desserts", "A sweet end to dinner", "desserts"),
    ("Beverages", "Cool drinks and coffee", "beverages"),
]

# (category, name, description, price, food_type)
ITEMS = [
    ("Chinese Starters", "Spring Rolls", "Crisp rolls filled with cabbage, carrot and glass noodles.", "149", "veg"),
    ("Chinese Starters", "Chilli Paneer", "Paneer cubes tossed with capsicum, onion and a spicy soy glaze.", "229", "veg"),
    ("Chinese Starters", "Chilli Chicken", "Crispy chicken in a hot garlic and green chilli sauce.", "269", "non_veg"),
    ("Chinese Starters", "Veg Manchurian", "Golden vegetable balls in a tangy ginger-garlic sauce.", "199", "veg"),
    ("Chinese Starters", "Chicken Manchurian", "Fried chicken in a bold, tangy Manchurian sauce.", "259", "non_veg"),
    ("Noodles", "Veg Hakka Noodles", "Thin noodles tossed with crunchy vegetables and soy.", "169", "veg"),
    ("Noodles", "Chicken Hakka Noodles", "Wok noodles with shredded chicken, egg and spring onion.", "209", "non_veg"),
    ("Fried Rice", "Veg Fried Rice", "Long-grain rice stir-fried with vegetables and spring onion.", "159", "veg"),
    ("Fried Rice", "Chicken Fried Rice", "Rice fried with chicken, egg and a hint of pepper.", "199", "non_veg"),
    ("Chinese Main Course", "Veg Manchurian Gravy", "Vegetable balls simmered in a thick Manchurian gravy.", "219", "veg"),
    ("Chinese Main Course", "Chicken in Hot Garlic Sauce", "Tender chicken in a deep garlic and chilli gravy.", "289", "non_veg"),
    ("Soups", "Hot and Sour Soup", "Peppery, tangy soup with vegetables and tofu.", "129", "veg"),
    ("Soups", "Chicken Sweet Corn Soup", "Silky soup with sweet corn and shredded chicken.", "149", "non_veg"),
    ("Momos", "Veg Momos", "Steamed dumplings with cabbage, carrot and herbs (8 pcs).", "119", "veg"),
    ("Momos", "Chicken Momos", "Steamed dumplings with juicy minced chicken (8 pcs).", "149", "non_veg"),
    ("Desserts", "Chocolate Brownie", "Warm fudgy brownie with a dusting of cocoa.", "129", "veg"),
    ("Desserts", "Honey Noodles with Ice Cream", "Crisp fried noodles in honey with vanilla ice cream.", "169", "veg"),
    ("Beverages", "Cold Coffee", "Chilled coffee blended with milk and ice.", "119", "veg"),
    ("Beverages", "Lemon Iced Tea", "Fresh lemon and black tea over ice.", "99", "veg"),
]


def seed(db: Session) -> None:
    cats: dict[str, Category] = {}
    slugs = {name: slug for name, _, slug in CATEGORIES}
    for name, desc, _ in CATEGORIES:
        cat = db.scalar(select(Category).where(Category.name == name))
        if not cat:
            cat = Category(name=name, description=desc)
            db.add(cat)
            db.flush()
        cats[name] = cat

    added = 0
    for cat_name, name, desc, price, ftype in ITEMS:
        if not db.scalar(select(MenuItem.id).where(MenuItem.name == name)):
            db.add(MenuItem(category_id=cats[cat_name].id, name=name, description=desc, price=Decimal(price),
                            food_type=ftype, image_url=f"/images/{slugs[cat_name]}.svg", is_available=True))
            added += 1

    s = get_settings()
    admin_msg = "admin not created (SEED_ADMIN_PASSWORD is empty)"
    if s.seed_admin_password:
        email = s.seed_admin_email.lower()
        if not db.scalar(select(User.id).where(User.email == email)):
            db.add(User(name="Dragon Wok Admin", email=email, phone="9999999999",
                        password_hash=hash_password(s.seed_admin_password), role="admin"))
            admin_msg = f"admin created: {email}"
        else:
            admin_msg = "admin already exists"
    db.commit()
    log.info("Seed finished: %s new menu items, %s", added, admin_msg)
    print(f"Seed finished: {added} new menu items, {admin_msg}")


if __name__ == "__main__":
    with SessionLocal() as session:
        seed(session)
