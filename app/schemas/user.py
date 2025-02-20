from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from app.schemas.check import CheckResponse


class CreateUserRequest(BaseModel):
    name: str = Field(min_length=1, max_length=512, examples=['Tester'])
    login: str = Field(min_length=4, max_length=512, examples=['test'],
                       description='Will be stored in lowercase')
    email: EmailStr
    password: str = Field(min_length=8, max_length=512)

    @field_validator('login', mode='after')
    @classmethod
    def lower_case(cls, value: str) -> str:
        return value.lower()


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
