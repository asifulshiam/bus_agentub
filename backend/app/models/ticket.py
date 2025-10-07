import enum

from sqlalchemy import DECIMAL, TIMESTAMP, Column, Enum, ForeignKey, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from ..database import Base


class TicketStatus(enum.Enum):
    confirmed = "confirmed"
    completed = "completed"
    cancelled = "cancelled"


class Ticket(Base):
    __tablename__ = "tickets"

    id = Column(Integer, primary_key=True, index=True)
    booking_id = Column(Integer, ForeignKey("bookings.id"), nullable=False, unique=True)
    boarding_point_id = Column(
        Integer, ForeignKey("boarding_points.id"), nullable=False
    )
    seats_booked = Column(Integer, nullable=False)
    fare_per_seat = Column(DECIMAL(10, 2), nullable=False)
    total_fare = Column(DECIMAL(10, 2), nullable=False)
    status = Column(Enum(TicketStatus), default=TicketStatus.confirmed, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)
    completed_at = Column(TIMESTAMP, nullable=True)
    cancelled_at = Column(TIMESTAMP, nullable=True)
    updated_at = Column(
        TIMESTAMP, server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationships
    booking = relationship("Booking", back_populates="ticket")
    boarding_point = relationship("BoardingPoint", back_populates="tickets")
