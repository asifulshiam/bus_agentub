from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, field_validator


class UserRole(str, Enum):
    """User role enum matching the database model"""

    PASSENGER = "passenger"
    SUPERVISOR = "supervisor"
    OWNER = "owner"


# Request Schemas
class UserRegister(BaseModel):
    """Schema for user registration"""

    name: str = Field(..., min_length=2, max_length=100)
    phone: str = Field(..., pattern=r"^\+?[0-9]{10,15}$")
    password: str = Field(..., min_length=8, max_length=100)
    nid: str = Field(..., min_length=10, max_length=20)
    role: UserRole = Field(default=UserRole.PASSENGER)

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        """Ensure phone number is clean"""
        # Remove any spaces or dashes
        return v.replace(" ", "").replace("-", "")

    class Config:
        json_schema_extra = {
            "example": {
                "name": "John Doe",
                "phone": "+8801712345678",
                "password": "SecurePass123",
                "nid": "1234567890123",
                "role": "passenger",
            }
        }


class UserLogin(BaseModel):
    """Schema for user login"""

    phone: str = Field(..., pattern=r"^\+?[0-9]{10,15}$")
    password: str = Field(..., min_length=8)

    class Config:
        json_schema_extra = {
            "example": {"phone": "+8801712345678", "password": "SecurePass123"}
        }


class UserUpdate(BaseModel):
    """Schema for updating user profile"""

    name: Optional[str] = Field(None, min_length=2, max_length=100)
    phone: Optional[str] = Field(None, pattern=r"^\+?[0-9]{10,15}$")
    password: Optional[str] = Field(None, min_length=8, max_length=100)

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: Optional[str]) -> Optional[str]:
        """Ensure phone number is clean"""
        if v:
            return v.replace(" ", "").replace("-", "")
        return v

    class Config:
        json_schema_extra = {
            "example": {"name": "John Updated", "phone": "+8801712345679"}
        }


# Response Schemas
class UserResponse(BaseModel):
    """Schema for user data in responses (NO NID, NO password)"""

    id: int
    name: str
    phone: str
    role: UserRole
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "name": "John Doe",
                "phone": "+8801712345678",
                "role": "passenger",
                "is_active": True,
                "created_at": "2025-10-01T10:00:00",
                "updated_at": "2025-10-01T10:00:00",
            }
        }


class TokenResponse(BaseModel):
    """Schema for JWT token response"""

    access_token: str
    token_type: str = "bearer"
    user: UserResponse
    assigned_buses: Optional[List[Dict[str, Any]]] = None  # ← ADD THIS LINE

    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "user": {
                    "id": 1,
                    "name": "John Doe",
                    "phone": "+8801712345678",
                    "role": "passenger",
                    "is_active": True,
                    "created_at": "2025-10-01T10:00:00",
                    "updated_at": "2025-10-01T10:00:00",
                },
            }
        }


class TokenData(BaseModel):
    """Schema for data stored in JWT token"""

    user_id: int
    phone: str
    role: UserRole
