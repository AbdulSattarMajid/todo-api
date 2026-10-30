"""SQLAlchemy ORM models — each class maps to one database table.

Every String has an explicit length: MySQL requires one, and MSSQL cannot index VARCHAR(max).
"""
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String

from app.core.constants import (
    EMAIL_MAX_LENGTH,
    ITEM_DESCRIPTION_MAX_LENGTH,
    ITEM_NAME_MAX_LENGTH,
    NAME_MAX_LENGTH,
    PASSWORD_HASH_MAX_LENGTH,
    ROLE_MAX_LENGTH,
    ROLE_USER,
    USERNAME_MAX_LENGTH,
)
from app.db.database import Base


class Users(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(EMAIL_MAX_LENGTH), unique=True, nullable=False)
    username = Column(String(USERNAME_MAX_LENGTH), unique=True, nullable=False)
    first_name = Column(String(NAME_MAX_LENGTH))
    last_name = Column(String(NAME_MAX_LENGTH))
    # Only the bcrypt hash is stored, never the plain password.
    hashed_password = Column(String(PASSWORD_HASH_MAX_LENGTH), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    role = Column(String(ROLE_MAX_LENGTH), default=ROLE_USER, nullable=False)


class Items(Base):
    """Example feature. Copy this pattern for each new resource, then delete it."""

    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(ITEM_NAME_MAX_LENGTH), nullable=False)
    description = Column(String(ITEM_DESCRIPTION_MAX_LENGTH), nullable=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
