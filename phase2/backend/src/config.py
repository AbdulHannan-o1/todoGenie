import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    SECRET_KEY: str = os.getenv("BETTER_AUTH_SECRET")
    if SECRET_KEY is None:
        raise ValueError("BETTER_AUTH_SECRET environment variable not set.")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days

settings = Settings()