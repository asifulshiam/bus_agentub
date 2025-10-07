import enum

from sqlalchemy import TIMESTAMP, Column, Enum, ForeignKey, Integer, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from ..database import Base


class BookingStatus(enum.Enum):
    pending = "pending"
    accepted = "accepted"
    rejected = "rejected"
    cancelled = "cancelled"


class Booking(Base):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)
    passenger_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    bus_id = Column(Integer, ForeignKey("buses.id"), nullable=False)
    status = Column(Enum(BookingStatus), default=BookingStatus.pending, nullable=False)
    request_time = Column(TIMESTAMP, server_default=func.now(), nullable=False)
    accepted_time = Column(TIMESTAMP, nullable=True)
    rejected_time = Column(TIMESTAMP, nullable=True)
    cancelled_time = Column(TIMESTAMP, nullable=True)
    rejection_reason = Column(Text, nullable=True)
    cancellation_reason = Column(Text, nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)
    updated_at = Column(
        TIMESTAMP, server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationships
    passenger = relationship("User", foreign_keys=[passenger_id])
    bus = relationship("Bus", back_populates="bookings")
    ticket = relationship("Ticket", back_populates="booking", uselist=False)
