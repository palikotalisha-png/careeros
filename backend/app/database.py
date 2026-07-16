from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from app.config import settings

# SQLite fallback keeps the scaffold runnable with zero infra.
connect_args = {}
url = settings.database_url
if url.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(url, pool_pre_ping=True, connect_args=connect_args)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()


def init_db() -> None:
    from app import models  # noqa: F401  ensure models are registered
    Base.metadata.create_all(bind=engine)
