from pydantic import BaseModel, EmailStr, Field
from datetime import datetime


class OrganizationCreate(BaseModel):
    organization_name: str = Field(..., min_length=3, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=6)

    class Config:
        json_schema_extra = {
            "example": {
                "organization_name": "TechCorp",
                "email": "admin@techcorp.com",
                "password": "securepassword123"
            }
        }


class OrganizationUpdate(BaseModel):
    organization_name: str = Field(..., min_length=3, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=6)


class OrganizationResponse(BaseModel):
    organization_name: str
    collection_name: str
    admin_email: str
    created_at: datetime
    message: str = "Success"

    class Config:
        json_schema_extra = {
            "example": {
                "organization_name": "TechCorp",
                "collection_name": "org_techcorp",
                "admin_email": "admin@techcorp.com",
                "created_at": "2025-12-12T08:23:00",
                "message": "Organization created successfully"
            }
        }


class OrganizationGet(BaseModel):
    organization_name: str
    collection_name: str
    admin_email: str
    created_at: datetime
    updated_at: datetime
