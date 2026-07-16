import logging
from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError, ProgrammingError, OperationalError
from sqlalchemy.orm import declarative_base, sessionmaker
from app.config import settings

log = logging.getLogger(__name__)

# SQLite fallback keeps the scaffold runnable with zero infra.
connect_args = {}
url = settings.database_url
if url.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(url, pool_pre_ping=True, connect_args=connect_args)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()


def init_db() -> None:
    """Create tables if they don't exist yet.

    On serverless platforms (Vercel, etc.) multiple function instances can cold-start
    concurrently on first traffic and race to run create_all() at the same moment. Postgres
    then raises a UniqueViolation on its system catalog (e.g. "pg_type_typname_nsp_index")
    when two instances try to create the same type/table simultaneously. That's harmless —
    it just means another instance is creating (or already created) the schema — so we
    swallow it here instead of crashing the request.
    """
    from app import models  # noqa: F401  ensure models are registered
    try:
        Base.metadata.create_all(bind=engine)
    except (IntegrityError, ProgrammingError, OperationalError) as e:
        log.warning("init_db(): create_all raced with another instance, continuing: %s", e)
