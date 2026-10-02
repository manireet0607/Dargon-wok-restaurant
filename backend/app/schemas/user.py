from datetime import datetime
import re

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

PHONE_RE = re.compile(r"^\+?[0-9]{10,15}$")


def clean_phone(v: str) -> str:
    v = re.sub(r"[\s\-()]", "", v)
    if not PHONE_RE.match(v):
        raise ValueError("Enter a valid phone number (10 to 15 digits).")
    return v


class UserCreate(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    email: EmailStr
    phone: str
    password: str = Field(min_length=8, max_length=72)

    _phone = field_validator("phone")(clean_phone)

    @field_validator("name")
    @classmethod
    def strip_name(cls, v: str) -> str:
        return v.strip()

    @field_validator("password")
    @classmethod
    def strong_enough(cls, v: str) -> str:
        if not (re.search(r"[A-Za-z]", v) and re.search(r"[0-9]", v)):
            raise ValueError("Password must contain at least one letter and one number.")
        return v


class UserLogin(BaseModel):
    # Plain string (not EmailStr) so any stored account email can always log in.
    email: str = Field(min_length=3, max_length=255)
    password: str = Field(min_length=1, max_length=72)


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    email: EmailStr
    phone: str
    role: str
    created_at: datetime


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut
