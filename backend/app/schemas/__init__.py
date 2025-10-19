"""
Pydantic schemas for request/response validation
"""

from app.schemas.user import (
    UserRole,
    UserRegister,
    UserLogin,
    UserUpdate,
    UserResponse,
    TokenResponse,
    TokenData
)

from app.schemas.bus import (
    BusType,
    BusCreate,
    BusUpdate,
    BusSearchFilters,
    BusPublicResponse,
    BusDetailedResponse,
    BusOwnerResponse,
    BoardingPointBasic,
    SupervisorBasic
)

from app.schemas.boarding_point import (
    BoardingPointCreate,
    BoardingPointUpdate,
    BoardingPointResponse,
    BoardingPointWithBus
)

__all__ = [
    # User schemas
    "UserRole",
    "UserRegister",
    "UserLogin",
    "UserUpdate",
    "UserResponse",
    "TokenResponse",
    "TokenData",
    # Bus schemas
    "BusType",
    "BusCreate",
    "BusUpdate",
    "BusSearchFilters",
    "BusPublicResponse",
    "BusDetailedResponse",
    "BusOwnerResponse",
    "BoardingPointBasic",
    "SupervisorBasic",
    # BoardingPoint schemas
    "BoardingPointCreate",
    "BoardingPointUpdate",
    "BoardingPointResponse",
    "BoardingPointWithBus",
]
