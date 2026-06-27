from datetime import datetime, timedelta, timezone

from jose import jwt
from passlib.context import CryptContext

from config import settings

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_DAYS = 7

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(subject: str | int) -> str:
    expires_at = datetime.now(timezone.utc) + timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)
    payload = {"sub": str(subject), "exp": expires_at}
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=ALGORITHM)
