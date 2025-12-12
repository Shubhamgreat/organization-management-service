from fastapi import APIRouter, HTTPException, status
from ..schemas.admin import AdminLogin, TokenResponse
from ..services.auth_service import AuthService

router = APIRouter(prefix="/admin", tags=["Admin Authentication"])


@router.post("/login", response_model=TokenResponse)
async def admin_login(credentials: AdminLogin):
    try:
        admin = await AuthService.authenticate_admin(
            email=credentials.email,
            password=credentials.password,
        )

        if not admin:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        access_token = AuthService.create_admin_token(admin)

        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            admin_email=admin["email"],
            organization_name=admin["organization_name"],
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )
