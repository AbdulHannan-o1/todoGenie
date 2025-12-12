from typing import Optional
from sqlmodel import Session
from backend.src.models.user import User
from backend.src.api.auth import get_password_hash

class UserService:
    def __init__(self, session: Session):
        self.session = session

    def create_user(self, user_create: User) -> User:
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
        return user

    def get_user_by_username(self, username: str) -> Optional[User]:
        return self.session.query(User).filter(User.username == username).first()

    def get_user_by_email(self, email: str) -> Optional[User]:
        return self.session.query(User).filter(User.email == email).first()

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        return self.session.query(User).filter(User.id == user_id).first()

    def update_user_role(self, user_id: int, new_role: str) -> Optional[User]:
        user = self.get_user_by_id(user_id)
        if user:
            user.role = new_role
            self.session.add(user)
            self.session.commit()
            self.session.refresh(user)
        return user
