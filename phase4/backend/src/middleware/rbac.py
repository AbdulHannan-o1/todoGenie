from fastapi import Depends, HTTPException, status
from phase2.backend.src.api.auth import get_current_user
from phase2.backend.src.models import User

def role_required(required_role: str):
    def role_checker(current_user: User = Depends(get_current_user)):
        if current_user.role != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Operation not permitted"
            )
        return current_user
    return role_checker

def admin_required():
    return role_required("Admin")

def standard_user_required():
    return role_required("Standard User")
