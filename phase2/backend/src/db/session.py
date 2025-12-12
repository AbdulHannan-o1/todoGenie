from typing import Generator
from sqlmodel import Session
from backend.src.db.engine import engine
import logging

logger = logging.getLogger(__name__)

def get_session() -> Generator[Session, None, None]:
    try:
        with Session(engine) as session:
            yield session
    except Exception as e:
        logger.error(f"Database session error: {e}")
        raise