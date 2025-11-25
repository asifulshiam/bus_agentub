import enum

from sqlalchemy import TIMESTAMP, Boolean, Column, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from ..database import Base


class UserRole(enum.Enum):
    passenger = "passenger"
    supervisor = "supervisor"
    owner = "owner"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    phone = Column(String(20), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    nid = Column(String(20), nullable=False)
    role = Column(Enum(UserRole), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)
    updated_at = Column(
        TIMESTAMP, server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # ✅ NEW: Link supervisor to owner who hired them
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    # ✅ NEW: Relationships for owner-supervisor link
    hired_supervisors = relationship(
        "User",
        foreign_keys="User.owner_id",
        back_populates="hired_by",
        cascade="all, delete",
    )

    hired_by = relationship(
        "User",
        foreign_keys=[owner_id],
        remote_side=[id],
        back_populates="hired_supervisors",
    )
