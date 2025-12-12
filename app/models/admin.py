from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


class AdminModel(BaseModel):
    email: EmailStr
    hashed_password: str
    organization_name: str
    organization_id: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = True

    class Config:
        json_schema_extra = {
            "example": {
                "email": "admin@example.com",
                "hashed_password": "$2b$12$...",
                "organization_name": "TechCorp",
                "created_at": "2025-12-12T08:23:00",
                "is_active": True
            }
        }
