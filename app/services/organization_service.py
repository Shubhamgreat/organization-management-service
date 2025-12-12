from typing import Optional, Dict, List
from datetime import datetime
from ..database import db
from ..utils.password_handler import PasswordHandler
import re


class OrganizationService:
    @staticmethod
    def _generate_collection_name(org_name: str) -> str:
        clean_name = re.sub(r"[^a-zA-Z0-9]", "_", org_name.lower())
        return f"org_{clean_name}"

    @staticmethod
    async def organization_exists(organization_name: str) -> bool:
        master_db = db.get_master_db()
        org = await master_db.organizations.find_one({"organization_name": organization_name})
        return org is not None

    @staticmethod
    async def admin_exists(email: str) -> bool:
        master_db = db.get_master_db()
        admin = await master_db.admins.find_one({"email": email})
        return admin is not None

    @classmethod
    async def create_organization(cls, organization_name: str, email: str, password: str) -> Dict:
        if await cls.organization_exists(organization_name):
            raise ValueError("Organization already exists")

        if await cls.admin_exists(email):
            raise ValueError("Admin email already registered")

        master_db = db.get_master_db()
        collection_name = cls._generate_collection_name(organization_name)
        hashed_password = PasswordHandler.hash_password(password)

        org_data = {
            "organization_name": organization_name,
            "collection_name": collection_name,
            "admin_email": email,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }

        org_result = await master_db.organizations.insert_one(org_data)
        org_id = str(org_result.inserted_id)

        admin_data = {
            "email": email,
            "hashed_password": hashed_password,
            "organization_name": organization_name,
            "organization_id": org_id,
            "created_at": datetime.utcnow(),
            "is_active": True,
        }

        await master_db.admins.insert_one(admin_data)

        org_collection = db.get_org_collection(collection_name)
        await org_collection.insert_one({
            "type": "metadata",
            "organization_name": organization_name,
            "initialized_at": datetime.utcnow(),
            "description": "Organization data collection",
        })

        org_data["_id"] = org_id
        return org_data

    @staticmethod
    async def get_organization(organization_name: str) -> Optional[Dict]:
        master_db = db.get_master_db()
        org = await master_db.organizations.find_one({"organization_name": organization_name})
        if org:
            org["_id"] = str(org["_id"])
        return org

    @classmethod
    async def update_organization(cls, old_org_name: str, new_org_name: str, email: str, password: str, admin_email: str) -> Dict:
        master_db = db.get_master_db()
        old_org = await master_db.organizations.find_one({"organization_name": old_org_name})
        if not old_org:
            raise ValueError("Organization not found")

        admin = await master_db.admins.find_one({"email": admin_email, "organization_name": old_org_name})
        if not admin:
            raise ValueError("Unauthorized: Admin does not belong to this organization")

        if old_org_name != new_org_name and await cls.organization_exists(new_org_name):
            raise ValueError("New organization name already exists")

        new_collection_name = cls._generate_collection_name(new_org_name)
        old_collection_name = old_org["collection_name"]

        old_collection = db.get_org_collection(old_collection_name)
        documents = await old_collection.find().to_list(length=None)

        if documents:
            new_collection = db.get_org_collection(new_collection_name)
            await new_collection.insert_many(documents)

        updated_data = {
            "organization_name": new_org_name,
            "collection_name": new_collection_name,
            "admin_email": email,
            "updated_at": datetime.utcnow(),
        }

        await master_db.organizations.update_one(
            {"organization_name": old_org_name},
            {"$set": updated_data},
        )

        hashed_password = PasswordHandler.hash_password(password)
        await master_db.admins.update_one(
            {"email": admin_email},
            {"$set": {
                "email": email,
                "hashed_password": hashed_password,
                "organization_name": new_org_name,
            }},
        )

        if old_org_name != new_org_name:
            await old_collection.drop()

        updated_data["created_at"] = old_org["created_at"]
        return updated_data

    @staticmethod
    async def delete_organization(organization_name: str, admin_email: str) -> bool:
        master_db = db.get_master_db()
        org = await master_db.organizations.find_one({"organization_name": organization_name})
        if not org:
            raise ValueError("Organization not found")

        admin = await master_db.admins.find_one({"email": admin_email, "organization_name": organization_name})
        if not admin:
            raise ValueError("Unauthorized: Admin does not belong to this organization")

        collection_name = org["collection_name"]
        org_collection = db.get_org_collection(collection_name)
        await org_collection.drop()

        await master_db.admins.delete_many({"organization_name": organization_name})
        result = await master_db.organizations.delete_one({"organization_name": organization_name})
        return result.deleted_count > 0

    @staticmethod
    async def list_all_organizations() -> List[Dict]:
        master_db = db.get_master_db()
        orgs = await master_db.organizations.find().to_list(length=100)
        for org in orgs:
            org["_id"] = str(org["_id"])
        return orgs
