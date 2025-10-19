from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import datetime
from decimal import Decimal
from enum import Enum


class BusType(str, Enum):
    """Bus type enum matching the database model"""
    AC = "AC"
    NON_AC = "Non-AC"
    AC_SLEEPER = "AC Sleeper"


# Request Schemas
class BusCreate(BaseModel):
    """Schema for creating a new bus"""
    bus_number: str = Field(..., min_length=3, max_length=20)
    route_from: str = Field(..., min_length=2, max_length=100)
    route_to: str = Field(..., min_length=2, max_length=100)
    departure_time: datetime
    bus_type: BusType
    fare: Decimal = Field(..., gt=0)
    seat_capacity: int = Field(..., gt=0, le=100)
    supervisor_id: Optional[int] = None

    @field_validator('route_from', 'route_to')
    @classmethod
    def validate_route(cls, v: str) -> str:
        """Ensure route names are properly formatted"""
        return v.strip().title()

    @field_validator('departure_time')
    @classmethod
    def validate_departure_time(cls, v: datetime) -> datetime:
        """Ensure departure time is in the future"""
        if v < datetime.now():
            raise ValueError('Departure time must be in the future')
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "bus_number": "DHA-1234",
                "route_from": "Dhaka",
                "route_to": "Chittagong",
                "departure_time": "2025-10-20T08:00:00",
                "bus_type": "AC",
                "fare": 850.00,
                "seat_capacity": 40,
                "supervisor_id": 2
            }
        }


class BusUpdate(BaseModel):
    """Schema for updating bus information (partial update)"""
    bus_number: Optional[str] = Field(None, min_length=3, max_length=20)
    route_from: Optional[str] = Field(None, min_length=2, max_length=100)
    route_to: Optional[str] = Field(None, min_length=2, max_length=100)
    departure_time: Optional[datetime] = None
    bus_type: Optional[BusType] = None
    fare: Optional[Decimal] = Field(None, gt=0)
    seat_capacity: Optional[int] = Field(None, gt=0, le=100)
    supervisor_id: Optional[int] = None
    is_active: Optional[bool] = None

    @field_validator('route_from', 'route_to')
    @classmethod
    def validate_route(cls, v: Optional[str]) -> Optional[str]:
        """Ensure route names are properly formatted"""
        if v:
            return v.strip().title()
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "fare": 900.00,
                "supervisor_id": 3
            }
        }


class BusSearchFilters(BaseModel):
    """Query parameters for searching buses"""
    route_from: Optional[str] = None
    route_to: Optional[str] = None
    bus_type: Optional[BusType] = None
    min_fare: Optional[Decimal] = Field(None, ge=0)
    max_fare: Optional[Decimal] = Field(None, ge=0)
    min_seats: Optional[int] = Field(None, ge=1)
    date: Optional[datetime] = None  # Filter by departure date
    sort_by: Optional[str] = Field(default="departure_time", pattern="^(fare|departure_time)$")
    order: Optional[str] = Field(default="asc", pattern="^(asc|desc)$")

    class Config:
        json_schema_extra = {
            "example": {
                "route_from": "Dhaka",
                "route_to": "Chittagong",
                "bus_type": "AC",
                "min_fare": 500,
                "max_fare": 1000,
                "min_seats": 10,
                "sort_by": "fare",
                "order": "asc"
            }
        }


# Response Schemas
class BusPublicResponse(BaseModel):
    """
    Public bus information (for search results)
    Does NOT include supervisor contact or exact location
    """
    id: int
    bus_number: str
    route_from: str
    route_to: str
    departure_time: datetime
    bus_type: BusType
    fare: Decimal
    available_seats: int
    is_active: bool

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "bus_number": "DHA-1234",
                "route_from": "Dhaka",
                "route_to": "Chittagong",
                "departure_time": "2025-10-20T08:00:00",
                "bus_type": "AC",
                "fare": 850.00,
                "available_seats": 35,
                "is_active": True
            }
        }


class BoardingPointBasic(BaseModel):
    """Basic boarding point info for bus details"""
    id: int
    name: str
    lat: Decimal
    lng: Decimal
    sequence_order: int

    class Config:
        from_attributes = True


class SupervisorBasic(BaseModel):
    """Basic supervisor info (only shown after booking acceptance)"""
    id: int
    name: str
    phone: str

    class Config:
        from_attributes = True


class BusDetailedResponse(BaseModel):
    """
    Detailed bus information (shown after booking acceptance)
    Includes supervisor contact and boarding points
    """
    id: int
    bus_number: str
    route_from: str
    route_to: str
    departure_time: datetime
    bus_type: BusType
    fare: Decimal
    seat_capacity: int
    available_seats: int
    owner_id: int
    supervisor: Optional[SupervisorBasic] = None
    boarding_points: List[BoardingPointBasic] = []
    current_lat: Optional[Decimal] = None
    current_lng: Optional[Decimal] = None
    last_location_update: Optional[datetime] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "bus_number": "DHA-1234",
                "route_from": "Dhaka",
                "route_to": "Chittagong",
                "departure_time": "2025-10-20T08:00:00",
                "bus_type": "AC",
                "fare": 850.00,
                "seat_capacity": 40,
                "available_seats": 35,
                "owner_id": 1,
                "supervisor": {
                    "id": 2,
                    "name": "John Supervisor",
                    "phone": "+8801812345678"
                },
                "boarding_points": [
                    {
                        "id": 1,
                        "name": "Mohakhali",
                        "lat": 23.7808,
                        "lng": 90.4044,
                        "sequence_order": 1
                    },
                    {
                        "id": 2,
                        "name": "Comilla",
                        "lat": 23.4607,
                        "lng": 91.1809,
                        "sequence_order": 2
                    }
                ],
                "current_lat": None,
                "current_lng": None,
                "last_location_update": None,
                "is_active": True,
                "created_at": "2025-10-11T10:00:00",
                "updated_at": "2025-10-11T10:00:00"
            }
        }


class BusOwnerResponse(BaseModel):
    """
    Bus information for owner dashboard
    Includes all details for management
    """
    id: int
    bus_number: str
    route_from: str
    route_to: str
    departure_time: datetime
    bus_type: BusType
    fare: Decimal
    seat_capacity: int
    available_seats: int
    supervisor_id: Optional[int] = None
    supervisor: Optional[SupervisorBasic] = None
    boarding_points_count: int = 0
    total_bookings: int = 0
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "bus_number": "DHA-1234",
                "route_from": "Dhaka",
                "route_to": "Chittagong",
                "departure_time": "2025-10-20T08:00:00",
                "bus_type": "AC",
                "fare": 850.00,
                "seat_capacity": 40,
                "available_seats": 35,
                "supervisor_id": 2,
                "supervisor": {
                    "id": 2,
                    "name": "John Supervisor",
                    "phone": "+8801812345678"
                },
                "boarding_points_count": 3,
                "total_bookings": 5,
                "is_active": True,
                "created_at": "2025-10-11T10:00:00",
                "updated_at": "2025-10-11T10:00:00"
            }
        }
