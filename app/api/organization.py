from fastapi import APIRouter, HTTPException, status, Depends
from typing import Dict
from ..schemas.organization import (
    OrganizationCreate,
    OrganizationResponse,
    OrganizationGet,
    OrganizationUpdate,
)
from ..services.organization_service import OrganizationService
from .dependencies import get_current_admin

router = APIRouter(prefix="/org", tags=["Organizations"])


@router.post("/create", response_model=OrganizationResponse, status_code=status.HTTP_201_CREATED)
async def create_organization(org_data: OrganizationCreate):
    try:
        result = await OrganizationService.create_organization(
            organization_name=org_data.organization_name,
            email=org_data.email,
            password=org_data.password,
        )

        return OrganizationResponse(
            organization_name=result["organization_name"],
            collection_name=result["collection_name"],
            admin_email=result["admin_email"],
            created_at=result["created_at"],
            message="Organization created successfully",
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/get", response_model=OrganizationGet)
async def get_organization(organization_name: str):
    try:
        org = await OrganizationService.get_organization(organization_name)

        if not org:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Organization not found",
            )

        return OrganizationGet(**org)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.put("/update", response_model=OrganizationResponse)
async def update_organization(
    old_organization_name: str,
    org_data: OrganizationUpdate,
    current_admin: Dict = Depends(get_current_admin),
):
    try:
        admin_email = current_admin["sub"]

        result = await OrganizationService.update_organization(
            old_org_name=old_organization_name,
            new_org_name=org_data.organization_name,
            email=org_data.email,
            password=org_data.password,
            admin_email=admin_email,
        )

        return OrganizationResponse(
            organization_name=result["organization_name"],
            collection_name=result["collection_name"],
            admin_email=result["admin_email"],
            created_at=result["created_at"],
            message="Organization updated successfully",
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.delete("/delete", status_code=status.HTTP_200_OK)
async def delete_organization(
    organization_name: str,
    current_admin: Dict = Depends(get_current_admin),
):
    try:
        admin_email = current_admin["sub"]

        success = await OrganizationService.delete_organization(
            organization_name=organization_name,
            admin_email=admin_email,
        )

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Organization not found",
            )

        return {"message": "Organization deleted successfully", "organization_name": organization_name}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
