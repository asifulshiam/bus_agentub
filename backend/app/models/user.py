import enum

from sqlalchemy import TIMESTAMP, Boolean, Column, Enum, Integer, String
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
    phone = Column(String(11), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    nid = Column(String(20), nullable=False)
    role = Column(Enum(UserRole), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)
    updated_at = Column(
        TIMESTAMP, server_default=func.now(), onupdate=func.now(), nullable=False
    )
