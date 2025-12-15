from sqlmodel import create_engine
from sqlalchemy.engine import Engine # Corrected import for Engine
import os

_engine: Engine | None = None

def create_db_engine(database_url: str | None = None) -> Engine:
    global _engine
    if database_url is None:
        database_url = os.environ.get("DATABASE_URL")
        if not database_url:
            raise ValueError("DATABASE_URL environment variable not set.")
    
    connect_args = {}
    if database_url.startswith("sqlite:///:memory:"):
        connect_args["check_same_thread"] = False
        
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

# Initialize the engine when the module is imported, using the environment variable
# This will be overridden by tests
engine = get_engine()