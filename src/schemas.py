from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, EmailStr, ConfigDict

from src.database.models import UserRole


class ContactBase(BaseModel):
    """
    Base class for contact schema. Pydantic model that represents a contact's basic information.
    """

    first_name: str = Field(max_length=50)
    last_name: str = Field(max_length=50)
    email: EmailStr
    phone_number: str = Field(max_length=20)
    birth_date: Optional[datetime] = None
    additional_info: Optional[str] = Field(max_length=255, default=None)


class ContactResponse(ContactBase):
    """
    Response class for contact schema. Pydantic model that represents a contact's basic information.
    """

    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class User(BaseModel):
    """Pydantic model that represents a user's basic information."""

    id: int
    username: str
    email: str
    avatar: str
    role: UserRole

    model_config = ConfigDict(from_attributes=True)


class UserCreate(BaseModel):
    """Pydantic model that represents the structure of data required to create a new user."""

    username: str
    email: str
    password: str
    role: UserRole


class Token(BaseModel):
    """Pydantic model that represents the structure of data returned after successful authentication."""

    access_token: str
    token_type: str


class RequestEmail(BaseModel):
    """Pydantic model that represents the structure of data required to send an email."""

    email: EmailStr


class ResetPassword(BaseModel):
    """Pydantic model that represents the structure of data required to reset a user's password."""

    token: str
    new_password: str = Field(min_length=8)
