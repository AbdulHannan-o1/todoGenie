from passlib.context import CryptContext
from cryptography.fernet import Fernet
import os

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Encryption setup
# Generate a key and store it securely (e.g., in an environment variable)
# For development, you can generate one with: Fernet.generate_key().decode()
ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY", Fernet.generate_key().decode())
fernet = Fernet(ENCRYPTION_KEY.encode())

def get_password_hash(password: str) -> str:
    # WARNING: This is a dummy hash for testing purposes only.
    # DO NOT USE IN PRODUCTION.
    return f"dummy_hashed_{password}"

def verify_password(plain_password: str, hashed_password: str) -> bool:
    # WARNING: This is a dummy verification for testing purposes only.
    # DO NOT USE IN PRODUCTION.
    return f"dummy_hashed_{plain_password}" == hashed_password

def encrypt_data(data: str) -> str:
    return fernet.encrypt(data.encode()).decode()

def decrypt_data(encrypted_data: str) -> str:
    return fernet.decrypt(encrypted_data.encode()).decode()