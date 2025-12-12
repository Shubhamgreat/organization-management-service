from typing import Optional, Dict
from datetime import timedelta
from ..database import db
from ..utils.password_handler import PasswordHandler
from ..utils.jwt_handler import JWTHandler
from ..config import get_settings

settings = get_settings()


class AuthService:
    @staticmethod
    async def authenticate_admin(email: str, password: str) -> Optional[Dict]:
        master_db = db.get_master_db()
        admin = await master_db.admins.find_one({"email": email})
        if not admin:
            return None

        if not PasswordHandler.verify_password(password, admin["hashed_password"]):
            return None

        if not admin.get("is_active", True):
            return None

        return admin

    @staticmethod
    def create_admin_token(admin: Dict) -> str:
        token_data = {
            "sub": admin["email"],
            "organization_name": admin["organization_name"],
            "organization_id": admin.get("organization_id", ""),
        }
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = JWTHandler.create_access_token(
            data=token_data,
            expires_delta=access_token_expires,
        )
        return access_token

    @staticmethod
    def verify_token(token: str) -> Optional[Dict]:
        return JWTHandler.decode_token(token)
