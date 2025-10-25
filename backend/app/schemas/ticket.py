from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime
from enum import Enum
from decimal import Decimal


class TicketStatus(str, Enum):
    """Ticket status enum matching the database model"""
    confirmed = "confirmed"
    completed = "completed"
    cancelled = "cancelled"


# Request Schemas
class TicketConfirmRequest(BaseModel):
    """Schema for confirming ticket details"""
    booking_id: int = Field(..., gt=0)
    boarding_point_id: int = Field(..., gt=0)
    seats_booked: int = Field(..., gt=0, le=10)  # Max 10 seats per booking

    class Config:
        json_schema_extra = {
            "example": {
                "booking_id": 1,
                "boarding_point_id": 1,
                "seats_booked": 2
            }
        }


class TicketCancelRequest(BaseModel):
    """Schema for cancelling a ticket"""
    ticket_id: int = Field(..., gt=0)
    reason: Optional[str] = Field(None, max_length=500)

    class Config:
        json_schema_extra = {
            "example": {
                "ticket_id": 1,
                "reason": "Change of plans"
            }
        }


# Response Schemas
class TicketResponse(BaseModel):
    """Schema for ticket in responses"""
    id: int
    booking_id: int
    boarding_point_id: int
    boarding_point_name: str
    boarding_point_lat: Decimal
    boarding_point_lng: Decimal
    boarding_point_sequence: int
    seats_booked: int
    fare_per_seat: Decimal
    total_fare: Decimal
    status: TicketStatus
    bus_number: str
    route_from: str
    route_to: str
    departure_time: datetime
    created_at: datetime
    completed_at: Optional[datetime] = None
    cancelled_at: Optional[datetime] = None

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "booking_id": 1,
                "boarding_point_id": 1,
                "boarding_point_name": "Mohakhali Bus Stand",
                "boarding_point_lat": 23.7808,
                "boarding_point_lng": 90.4044,
                "boarding_point_sequence": 1,
                "seats_booked": 2,
                "fare_per_seat": 850.00,
                "total_fare": 1700.00,
                "status": "confirmed",
                "bus_number": "DHA-1234",
                "route_from": "Dhaka",
                "route_to": "Chittagong",
                "departure_time": "2025-10-20T08:00:00",
                "created_at": "2025-10-11T10:00:00",
                "completed_at": None,
                "cancelled_at": None
            }
        }


class TicketConfirmResponse(BaseModel):
    """Response after confirming ticket"""
    ticket_id: int
    status: TicketStatus
    seats_booked: int
    total_fare: Decimal
    boarding_point: dict
    bus_details: dict
    message: str

    class Config:
        json_schema_extra = {
            "example": {
                "ticket_id": 1,
                "status": "confirmed",
                "seats_booked": 2,
                "total_fare": 1700.00,
                "boarding_point": {
                    "id": 1,
                    "name": "Mohakhali Bus Stand",
                    "lat": 23.7808,
                    "lng": 90.4044,
                    "sequence_order": 1
                },
                "bus_details": {
                    "bus_number": "DHA-1234",
                    "route_from": "Dhaka",
                    "route_to": "Chittagong",
                    "departure_time": "2025-10-20T08:00:00"
                },
                "message": "Ticket confirmed successfully"
            }
        }


class TicketStatusResponse(BaseModel):
    """Simple ticket status response"""
    ticket_id: int
    status: TicketStatus
    message: str

    class Config:
        json_schema_extra = {
            "example": {
                "ticket_id": 1,
                "status": "cancelled",
                "message": "Ticket cancelled successfully"
            }
        }
