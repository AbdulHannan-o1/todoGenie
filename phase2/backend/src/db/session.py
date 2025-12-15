from typing import Generator
from sqlmodel import Session
from phase2.backend.src.db.engine import engine
import logging

logger = logging.getLogger(__name__)

def get_session() -> Generator[Session, None, None]:
    print(f"Using engine: {engine}") # Added print statement
    try:
        with Session(engine) as session:
            yield session
    except Exception as e:
        logger.error(f"Database session error: {e}")
        raise