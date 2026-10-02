import logging
import time
import uuid

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text

from app.api.v1.router import api_router
from app.core.config import get_settings
from app.core.logging import setup_logging
from app.db.session import engine

settings = get_settings()
setup_logging(settings.log_level)
settings.validate_for_runtime()
log = logging.getLogger("dragonwok")

app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    # Hide interactive docs in production
    docs_url=None if settings.is_production else "/docs",
    redoc_url=None,
    openapi_url=None if settings.is_production else "/openapi.json",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=False,  # we use Authorization headers, not cookies
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)


@app.middleware("http")
async def request_logger(request: Request, call_next):
    request_id = request.headers.get("x-request-id") or uuid.uuid4().hex[:12]
    start = time.perf_counter()
    try:
        response = await call_next(request)
    except Exception:
        log.exception("Unhandled error", extra={"request_id": request_id, "method": request.method, "path": request.url.path})
        response = JSONResponse({"detail": "Something went wrong on our side. Please try again."}, status_code=500)
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Content-Type-Options"] = "nosniff"
    if request.url.path != "/health":
        log.info(
            "request",
            extra={"request_id": request_id, "method": request.method, "path": request.url.path,
                   "status": response.status_code, "duration_ms": round((time.perf_counter() - start) * 1000, 1)},
        )
    return response


@app.get("/health", tags=["health"])
def health():
    """Liveness check (load balancer / ECS container health check)."""
    return {"status": "ok"}


@app.get("/health/ready", tags=["health"])
def ready():
    """Readiness check: also tests the database connection."""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
    except Exception:
        log.exception("Database readiness check failed")
        return JSONResponse({"status": "unavailable"}, status_code=503)
    return {"status": "ready"}


app.include_router(api_router, prefix=settings.api_v1_prefix)
