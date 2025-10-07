from sqlalchemy import DECIMAL, TIMESTAMP, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from ..database import Base


class BoardingPoint(Base):
    __tablename__ = "boarding_points"

    id = Column(Integer, primary_key=True, index=True)
    bus_id = Column(Integer, ForeignKey("buses.id"), nullable=False)
    name = Column(String(100), nullable=False)
    lat = Column(DECIMAL(10, 8), nullable=False)
    lng = Column(DECIMAL(11, 8), nullable=False)
    sequence_order = Column(Integer, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)

    # Relationships
    bus = relationship("Bus", back_populates="boarding_points")
    tickets = relationship("Ticket", back_populates="boarding_point")
