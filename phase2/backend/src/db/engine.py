from sqlmodel import create_engine
import os

DATABASE_URL = os.environ.get("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable not set.")

# For data encryption in transit (SSL), configure the DATABASE_URL with appropriate SSL parameters (e.g., ?sslmode=require).
# Data encryption at rest is typically handled by the database provider (e.g., Neon).
engine = create_engine(DATABASE_URL, echo=True)

def get_engine():
    return engine