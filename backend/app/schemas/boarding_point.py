from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from decimal import Decimal


# Request Schemas
class BoardingPointCreate(BaseModel):
    """Schema for creating a new boarding point"""
    name: str = Field(..., min_length=2, max_length=100)
    lat: Decimal = Field(..., ge=-90, le=90)
    lng: Decimal = Field(..., ge=-180, le=180)
    sequence_order: int = Field(..., gt=0)

    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Ensure boarding point name is properly formatted"""
        return v.strip().title()

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Mohakhali Bus Stand",
                "lat": 23.7808,
                "lng": 90.4044,
                "sequence_order": 1
            }
        }


class BoardingPointUpdate(BaseModel):
    """Schema for updating boarding point (partial update)"""
    name: str | None = Field(None, min_length=2, max_length=100)
    lat: Decimal | None = Field(None, ge=-90, le=90)
    lng: Decimal | None = Field(None, ge=-180, le=180)
    sequence_order: int | None = Field(None, gt=0)

    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str | None) -> str | None:
        """Ensure boarding point name is properly formatted"""
        if v:
            return v.strip().title()
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Updated Stop Name",
                "sequence_order": 2
            }
        }


# Response Schemas
class BoardingPointResponse(BaseModel):
    """Schema for boarding point in responses"""
    id: int
    bus_id: int
    name: str
    lat: Decimal
    lng: Decimal
    sequence_order: int
    created_at: datetime

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "bus_id": 1,
                "name": "Mohakhali Bus Stand",
                "lat": 23.7808,
                "lng": 90.4044,
                "sequence_order": 1,
                "created_at": "2025-10-11T10:00:00"
            }
        }


class BoardingPointWithBus(BaseModel):
    """Schema for boarding point with basic bus info"""
    id: int
    bus_id: int
    name: str
    lat: Decimal
    lng: Decimal
    sequence_order: int
    bus_number: str  # From relationship
    route_from: str  # From relationship
    route_to: str    # From relationship
    created_at: datetime

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "bus_id": 1,
                "name": "Mohakhali Bus Stand",
                "lat": 23.7808,
                "lng": 90.4044,
                "sequence_order": 1,
                "bus_number": "DHA-1234",
                "route_from": "Dhaka",
                "route_to": "Chittagong",
                "created_at": "2025-10-11T10:00:00"
            }
        }
