from datetime import datetime, timedelta, timezone
from typing import Any
from enum import Enum
from passlib.context import CryptContext
import jwt

from app.core.config import settings

pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")


class TokenType(Enum):
    ACCESS_TOKEN = 'access_token'
    REFRESH_TOKEN = 'refresh_token'


def hash_password(password: str) -> str:
    return pwd_ctx.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_ctx.verify(plain_password, hashed_password)


def create_jwt_token(
    subject: str | Any, expire_delta: timedelta, token_type: TokenType
) -> str:
    expire = datetime.now(timezone.utc) + expire_delta
    to_encode = {'exp': expire, 'sub': str(subject), 'token_type': token_type.value}
    encoded_jwt = jwt.encode(
        to_encode, settings.JWT_SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def decode_jwt_token(token):
    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET_KEY, algorithms=settings.ALGORITHM
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise
    except jwt.InvalidTokenError:
        raise


def is_refresh_token(payload: dict) -> bool:
    return payload.get("token_type") == TokenType.REFRESH_TOKEN.value
