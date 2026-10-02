from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import get_settings


def build_engine() -> Engine:
    s = get_settings()
    url = s.sqlalchemy_url
    kwargs: dict = {"pool_pre_ping": True, "pool_recycle": s.db_pool_recycle}
    if url.startswith("mysql"):
        kwargs["pool_size"] = s.db_pool_size
        kwargs["max_overflow"] = 10
        if s.db_ssl_enabled:
            # PyMySQL TLS: verify the server certificate (and host name) against the RDS CA bundle.
            kwargs["connect_args"] = {
                "ssl_ca": s.db_ssl_ca,
                "ssl_verify_cert": True,
                "ssl_verify_identity": s.db_ssl_verify_identity,
            }
    elif url.startswith("sqlite"):
        kwargs = {"connect_args": {"check_same_thread": False}}
    return create_engine(url, **kwargs)


engine = build_engine()
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
