from typing import List

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.user import UserRole
from app.utils import decode_access_token

security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    """
    Dependency to get the currently authenticated user

    Args:
        credentials: Bearer token from Authorization header
        db: Database session

    Returns:
        User object if authenticated

    Raises:
        HTTPException: If token is invalid or user not found
    """
    token = credentials.credentials

    # Decode token
    token_data = decode_access_token(token)
    if token_data is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Get user from database
    user = db.query(User).filter(User.id == token_data.user_id).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="User account is inactive"
        )

    return user


def require_roles(allowed_roles: List[UserRole]):
    """
    Dependency factory to require specific user roles

    Args:
        allowed_roles: List of allowed UserRole enums

    Returns:
        Dependency function that checks user role

    Example:
        @app.get("/admin")
        def admin_route(user: User = Depends(require_roles([UserRole.OWNER]))):
            ...
    """

    def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required roles: {[role.value for role in allowed_roles]}",
            )
        return current_user

    return role_checker


# Convenience dependencies for specific roles
def get_current_passenger(current_user: User = Depends(get_current_user)) -> User:
    """Dependency to ensure current user is a passenger"""
    if current_user.role != UserRole.PASSENGER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only passengers can access this endpoint",
        )
    return current_user


def get_current_supervisor(current_user: User = Depends(get_current_user)) -> User:
    """Dependency to ensure current user is a supervisor"""
    if current_user.role != UserRole.SUPERVISOR:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only supervisors can access this endpoint",
        )
    return current_user


def get_current_owner(current_user: User = Depends(get_current_user)) -> User:
    """Dependency to ensure current user is an owner"""
    if current_user.role != UserRole.OWNER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only owners can access this endpoint",
        )
    return current_user
