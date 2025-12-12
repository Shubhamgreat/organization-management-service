from pydantic import BaseModel, Field
from datetime import datetime


class OrganizationModel(BaseModel):
    organization_name: str
    collection_name: str
    admin_email: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_schema_extra = {
            "example": {
                "organization_name": "TechCorp",
                "collection_name": "org_techcorp",
                "admin_email": "admin@techcorp.com",
                "created_at": "2025-12-12T08:23:00",
                "updated_at": "2025-12-12T08:23:00"
            }
        }
