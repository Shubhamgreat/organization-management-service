from passlib.context import CryptContext


class PasswordHandler:
    # Use pbkdf2_sha256 instead of bcrypt to avoid 72‑byte limit
    pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

    @classmethod
    def hash_password(cls, password: str) -> str:
        return cls.pwd_context.hash(password)

    @classmethod
    def verify_password(cls, plain_password: str, hashed_password: str) -> bool:
        return cls.pwd_context.verify(plain_password, hashed_password)
