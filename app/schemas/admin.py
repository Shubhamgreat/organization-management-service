from pydantic import BaseModel, EmailStr, Field


class AdminLogin(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)

    class Config:
        json_schema_extra = {
            "example": {
                "email": "admin@techcorp.com",
                "password": "securepassword123"
            }
        }


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    admin_email: str
    organization_name: str

    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
            "token_type": "bearer",
            "admin_email": "admin@techcorp.com",
            "organization_name": "TechCorp"
            }
        }
