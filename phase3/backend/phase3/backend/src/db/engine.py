from sqlmodel import create_engine
from sqlalchemy.engine import Engine
import os

_engine: Engine | None = None

def create_db_engine(database_url: str | None = None) -> Engine:
    global _engine
    if database_url is None:
        database_url = os.environ.get("DATABASE_URL")
        if not database_url:
            raise ValueError("DATABASE_URL environment variable not set.")

    connect_args = {}
    if database_url.startswith("sqlite://"):
        # SQLite-specific settings
        connect_args["check_same_thread"] = False
    elif database_url.startswith("postgresql://") or database_url.startswith("postgresql+psycopg://"):
        # PostgreSQL-specific settings for Neon
        connect_args["sslmode"] = "require"

    _engine = create_engine(database_url, echo=True, connect_args=connect_args)
    return _engine

def get_engine() -> Engine:
    global _engine
    if _engine is None:
        _engine = create_db_engine() # Initialize if not already set
    return _engine

def set_test_engine(test_engine: Engine):
    global _engine
    _engine = test_engine

# Don't initialize the engine when the module is imported to allow tests to override it
# This will be initialized when get_engine() is called
# engine = get_engine()