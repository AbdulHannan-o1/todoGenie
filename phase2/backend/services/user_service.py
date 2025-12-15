from sqlmodel import Session, select
from phase2.backend.models import User
from phase2.backend.utils import get_password_hash

def create_db_user(user_data: dict, session: Session):
    user = User(email=user_data["email"], hashed_password=get_password_hash(user_data["password"]))
    session.add(user)
    session.commit()
    session.refresh(user)
    return user

def get_user_by_email(email: str, session: Session):
    return session.exec(select(User).where(User.email == email)).first()
