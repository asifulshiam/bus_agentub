from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.user import (
    TokenResponse,
    UserLogin,
    UserRegister,
    UserResponse,
    UserUpdate,
)
from app.utils import create_access_token, hash_password, verify_password

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED
)
def register_user(user_data: UserRegister, db: Session = Depends(get_db)):
    """
    Register a new user

    - **name**: Full name (2-100 characters)
    - **phone**: Phone number (unique, 10-15 digits)
    - **password**: Password (min 8 characters)
    - **nid**: National ID (10-20 characters, stored but never exposed)
    - **role**: User role (passenger/owner only - supervisors must be registered by owners)

    Returns JWT token and user data
    
    Note: Supervisors cannot self-register. They must be registered by a bus owner
    via the /owner/register-supervisor endpoint.
    """
    # ✅ SECURITY: Block supervisor self-registration
    if user_data.role.value == "supervisor":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Supervisors cannot self-register. Please contact a bus owner to create your account.",
        )

    # Check if phone already exists
    existing_user = db.query(User).filter(User.phone == user_data.phone).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Phone number already registered",
        )

    # Create new user (passengers and owners only)
    new_user = User(
        name=user_data.name,
        phone=user_data.phone,
        password_hash=hash_password(user_data.password),
        nid=user_data.nid,
        role=user_data.role,
        is_active=True,
        # owner_id stays NULL for passengers and owners
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Generate JWT token
    access_token = create_access_token(
        data={
            "user_id": new_user.id,
            "phone": new_user.phone,
            "role": new_user.role.value,
        },
        expires_delta=timedelta(days=settings.ACCESS_TOKEN_EXPIRE_DAYS),
    )

    # Convert to response schema (excludes NID and password)
    user_response = UserResponse.model_validate(new_user)

    return TokenResponse(
        access_token=access_token, token_type="bearer", user=user_response
    )


@router.post("/login", response_model=TokenResponse)
def login_user(login_data: UserLogin, db: Session = Depends(get_db)):
    """
    Login with phone and password

    - **phone**: Registered phone number
    - **password**: User password

    Returns JWT token and user data
    """
    # Find user by phone
    user = db.query(User).filter(User.phone == login_data.phone).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid phone or password"
        )

    # Verify password
    if not verify_password(login_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid phone or password"
        )

    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive. Please contact support.",
        )

    # Generate JWT token
    access_token = create_access_token(
        data={"user_id": user.id, "phone": user.phone, "role": user.role.value},
        expires_delta=timedelta(days=settings.ACCESS_TOKEN_EXPIRE_DAYS),
    )

    # Convert to response schema
    user_response = UserResponse.model_validate(user)

    return TokenResponse(
        access_token=access_token, token_type="bearer", user=user_response
    )


@router.get("/profile", response_model=UserResponse)
def get_profile(current_user: User = Depends(get_current_user)):
    """
    Get current user's profile

    Requires authentication (Bearer token in Authorization header)
    """
    return UserResponse.model_validate(current_user)


@router.put("/profile", response_model=UserResponse)
def update_profile(
    update_data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Update current user's profile

    - **name**: New name (optional)
    - **phone**: New phone number (optional, must be unique)
    - **password**: New password (optional)

    Requires authentication (Bearer token in Authorization header)
    """
    # Check if new phone already exists (if phone is being updated)
    if update_data.phone and update_data.phone != current_user.phone:
        existing_user = db.query(User).filter(User.phone == update_data.phone).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Phone number already in use",
            )
        current_user.phone = update_data.phone

    # Update name if provided
    if update_data.name:
        current_user.name = update_data.name

    # Update password if provided
    if update_data.password:
        current_user.password_hash = hash_password(update_data.password)

    db.commit()
    db.refresh(current_user)

    return UserResponse.model_validate(current_user)