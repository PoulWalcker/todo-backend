from pydantic import BaseModel, Field, EmailStr, field_validator
from enum import Enum


class Role(Enum):
    guest = 'guest'
    user = 'user'
    admin = 'admin'


class UpdateRole(BaseModel):
    role: Role = Field(default=None, description='User Role')


class User(BaseModel):
    first_name: str = Field(
        ..., min_length=3, max_length=100, description='User first name'
    )
    last_name: str = Field(
        ..., min_length=3, max_length=150, description='User last name'
    )
    email: EmailStr = Field(..., min_length=5, max_length=150, description='User email')

    @classmethod
    @field_validator("email")
    def norm_email(cls, v):
        return v.strip().lower()

    class Config:
        use_enum_values = True


class PublicUser(User):
    user_id: str = Field(..., description='User ID')


class PublicUsers(BaseModel):
    users: list[PublicUser]
    count: int


class DBUser(User):
    user_id: str = Field(..., description='User ID')
    hashed_password: str
    role: Role = Field(..., description='User Role')


class LoginUser(BaseModel):
    email: EmailStr = Field(..., min_length=5, max_length=150, description='User email')
    password: str = Field(..., description='User password')

    @classmethod
    @field_validator("email")
    def norm_email(cls, v):
        return v.strip().lower()


class CreateUser(User):
    password: str = Field(..., description='User password')


class UpdateUser(BaseModel):
    first_name: str | None = Field(
        default=None, min_length=3, max_length=100, description='User first name'
    )
    last_name: str | None = Field(
        default=None, min_length=3, max_length=150, description='User last name'
    )
    email: EmailStr | None = Field(
        default=None, min_length=5, max_length=150, description='User email'
    )
    password: str | None = Field(default=None, description='User password')

    @classmethod
    @field_validator("email")
    def norm_email(cls, v):
        return v.strip().lower()
