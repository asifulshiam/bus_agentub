from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import datetime
from enum import Enum
from decimal import Decimal


class BookingStatus(str, Enum):
    """Booking status enum matching the database model"""
    pending = "pending"
    accepted = "accepted"
    rejected = "rejected"
    cancelled = "cancelled"


# Request Schemas
class BookingRequestCreate(BaseModel):
    """Schema for creating a booking request"""
    bus_id: int = Field(..., gt=0)

    class Config:
        json_schema_extra = {
            "example": {
                "bus_id": 1
            }
        }


class BookingAcceptRequest(BaseModel):
    """Schema for accepting a booking"""
    booking_id: int = Field(..., gt=0)

    class Config:
        json_schema_extra = {
            "example": {
                "booking_id": 1
            }
        }


class BookingRejectRequest(BaseModel):
    """Schema for rejecting a booking"""
    booking_id: int = Field(..., gt=0)
    reason: Optional[str] = Field(None, max_length=500)

    class Config:
        json_schema_extra = {
            "example": {
                "booking_id": 1,
                "reason": "No seats available"
            }
        }


class BookingCancelRequest(BaseModel):
    """Schema for cancelling a booking"""
    booking_id: int = Field(..., gt=0)
    reason: Optional[str] = Field(None, max_length=500)

    class Config:
        json_schema_extra = {
            "example": {
                "booking_id": 1,
                "reason": "Change of plans"
            }
        }


# Response Schemas
class BookingBasicResponse(BaseModel):
    """Basic booking info for supervisor requests list"""
    id: int
    bus_id: int
    status: BookingStatus
    request_time: datetime

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "bus_id": 1,
                "status": "pending",
                "request_time": "2025-10-11T10:00:00"
            }
        }


class BookingDetailedResponse(BaseModel):
    """Detailed booking info shown after acceptance"""
    id: int
    bus_id: int
    passenger_id: int
    passenger_name: str
    passenger_phone: str
    status: BookingStatus
    request_time: datetime
    accepted_time: Optional[datetime] = None
    rejected_time: Optional[datetime] = None
    cancelled_time: Optional[datetime] = None
    rejection_reason: Optional[str] = None
    cancellation_reason: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "bus_id": 1,
                "passenger_id": 5,
                "passenger_name": "John Doe",
                "passenger_phone": "+8801712345678",
                "status": "accepted",
                "request_time": "2025-10-11T10:00:00",
                "accepted_time": "2025-10-11T10:05:00",
                "rejected_time": None,
                "cancelled_time": None,
                "rejection_reason": None,
                "cancellation_reason": None,
                "created_at": "2025-10-11T10:00:00",
                "updated_at": "2025-10-11T10:05:00"
            }
        }


class BookingAcceptanceResponse(BaseModel):
    """Response after accepting a booking"""
    booking_id: int
    status: BookingStatus
    passenger_name: str
    passenger_phone: str
    available_boarding_points: List[dict]  # Will be populated by the endpoint

    class Config:
        json_schema_extra = {
            "example": {
                "booking_id": 1,
                "status": "accepted",
                "passenger_name": "John Doe",
                "passenger_phone": "+8801712345678",
                "available_boarding_points": [
                    {
                        "id": 1,
                        "name": "Mohakhali Bus Stand",
                        "lat": 23.7808,
                        "lng": 90.4044,
                        "sequence_order": 1
                    }
                ]
            }
        }


class BookingStatusResponse(BaseModel):
    """Simple status response"""
    booking_id: int
    status: BookingStatus
    message: str

    class Config:
        json_schema_extra = {
            "example": {
                "booking_id": 1,
                "status": "accepted",
                "message": "Booking accepted successfully"
            }
        }
