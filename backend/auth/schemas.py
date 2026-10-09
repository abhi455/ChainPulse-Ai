from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    organization_id: str
    name: str = Field(min_length=2, max_length=150)
    email: EmailStr
    password: str = Field(min_length=8, max_length=72)
    role: str = Field(default="user", min_length=1, max_length=50)


class OnboardRequest(BaseModel):
    """
    Creates a new organization and its first administrator.
    """

    organization_name: str = Field(
        min_length=1,
        max_length=150,
    )

    name: str = Field(
        min_length=2,
        max_length=150,
    )

    email: EmailStr

    password: str = Field(
        min_length=8,
        max_length=72,
    )


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=72)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    id: str
    organization_id: str
    name: str
    email: str
    role: str
    is_active: bool
