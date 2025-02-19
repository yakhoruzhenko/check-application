from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.schemas.check import CheckResponse


class CreateUserRequest(BaseModel):
    name: str = Field(min_length=1, max_length=512, examples=['Tester'])
    login: str = Field(min_length=4, max_length=512, examples=['test'])
    email: EmailStr
    password: str = Field(min_length=8, max_length=512)


class ResetUserPasswordRequest(BaseModel):
    new_password: str = Field(min_length=8, max_length=512)


class ResetUserPassword(ResetUserPasswordRequest):
    user_id: UUID


class UserResponse(BaseModel):
    id: UUID
    name: str = Field(examples=['Tester'])
    login: str = Field(examples=['test'])
    email: str = Field(examples=['test@mail.com'])
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserResponseWithChecks(UserResponse):
    checks: list[CheckResponse]
