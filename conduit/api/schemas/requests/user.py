from typing import Any

from pydantic import BaseModel, EmailStr, Field, field_validator


class UserRegistrationData(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    username: str = Field(..., min_length=3)


class UserLoginData(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)


class UserUpdateData(BaseModel):
    email: EmailStr | None = Field(None)
    password: str | None = Field(None, min_length=8)
    username: str | None = Field(None, min_length=3)
    bio: str | None = Field(None)
    image: str | None = Field(None)

    @field_validator("*", mode="before")
    @classmethod
    def empty_as_none(cls, v: Any) -> Any:
        return v or None if isinstance(v, (str,)) else v


class UserRegistrationRequest(BaseModel):
    user: UserRegistrationData


class UserLoginRequest(BaseModel):
    user: UserLoginData


class UserUpdateRequest(BaseModel):
    user: UserUpdateData
