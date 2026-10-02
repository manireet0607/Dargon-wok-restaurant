from fastapi import APIRouter

from app.api.v1 import admin, auth, orders, public, users

api_router = APIRouter()
for r in (auth.router, users.router, public.router, orders.router, admin.router):
    api_router.include_router(r)
