from typing import Optional
from sqlmodel import Session
from backend.src.models.user import User
from backend.src.api.auth import get_password_hash
import logging

logger = logging.getLogger(__name__)

class UserService:
    def __init__(self, session: Session):
        self.session = session

    def create_user(self, user_create: User) -> User:
        try:
            hashed_password = get_password_hash(user_create.password_hash)
            user = User(
                username=user_create.username,
                email=user_create.email,
                password_hash=hashed_password,
                role=user_create.role
            )
            self.session.add(user)
            self.session.commit()
            self.session.refresh(user)
            logger.info(f"User created: {user.username}")
            return user
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            raise

    def get_user_by_username(self, username: str) -> Optional[User]:
        try:
            user = self.session.query(User).filter(User.username == username).first()
            if user:
                logger.info(f"User fetched by username: {username}")
            else:
                logger.warning(f"User not found by username: {username}")
            return user
        except Exception as e:
            logger.error(f"Error fetching user by username {username}: {e}")
            raise

    def get_user_by_email(self, email: str) -> Optional[User]:
        try:
            user = self.session.query(User).filter(User.email == email).first()
            if user:
                logger.info(f"User fetched by email: {email}")
            else:
                logger.warning(f"User not found by email: {email}")
            return user
        except Exception as e:
            logger.error(f"Error fetching user by email {email}: {e}")
            raise

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        try:
            user = self.session.query(User).filter(User.id == user_id).first()
            if user:
                logger.info(f"User fetched by id: {user_id}")
            else:
                logger.warning(f"User not found by id: {user_id}")
            return user
        except Exception as e:
            logger.error(f"Error fetching user by id {user_id}: {e}")
            raise

    def update_user_role(self, user_id: int, new_role: str) -> Optional[User]:
        try:
            user = self.get_user_by_id(user_id)
            if user:
                user.role = new_role
                self.session.add(user)
                self.session.commit()
                self.session.refresh(user)
                logger.info(f"User role updated for user: {user_id}")
            return user
        except Exception as e:
            logger.error(f"Error updating user role for user {user_id}: {e}")
            raise
