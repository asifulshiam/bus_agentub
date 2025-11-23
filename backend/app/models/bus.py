import enum

from sqlalchemy import (
    DECIMAL,
    TIMESTAMP,
    Boolean,
    Column,
    Enum,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from ..database import Base


class BusType(enum.Enum):
    AC = "AC"
    NON_AC = "Non-AC"
    AC_SLEEPER = "AC Sleeper"


class Bus(Base):
    __tablename__ = "buses"

    id = Column(Integer, primary_key=True, index=True)
    bus_number = Column(String(20), unique=True, nullable=False, index=True)
    route_from = Column(String(100), nullable=False)
    route_to = Column(String(100), nullable=False)
    departure_time = Column(TIMESTAMP, nullable=False)
    # FIX: Tell SQLAlchemy to use enum VALUES not NAMES
    bus_type = Column(
        Enum(BusType, values_callable=lambda x: [e.value for e in x]), nullable=False
    )
    fare = Column(DECIMAL(10, 2), nullable=False)
    seat_capacity = Column(Integer, nullable=False)
    available_seats = Column(Integer, nullable=False)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    supervisor_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    current_lat = Column(DECIMAL(10, 8), nullable=True)
    current_lng = Column(DECIMAL(11, 8), nullable=True)
    last_location_update = Column(TIMESTAMP, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)
    updated_at = Column(
        TIMESTAMP, server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationships
    owner = relationship("User", foreign_keys=[owner_id])
    supervisor = relationship("User", foreign_keys=[supervisor_id])
    boarding_points = relationship("BoardingPoint", back_populates="bus")
    bookings = relationship("Booking", back_populates="bus")
