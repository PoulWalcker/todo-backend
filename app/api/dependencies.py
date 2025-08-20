from uuid import UUID
import jwt
from typing import Annotated
from sqlite3 import Connection

from fastapi import Request, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from app.core.config import settings
from app.core.db import get_db
from app.core.security import decode_jwt_token, TokenType
from app.schemas.users import DBUser, Role
from app.crud.users import get_user_by_id_query

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/signin")

SessionDep = Annotated[Connection, Depends(get_db)]
TokenDep = Annotated[str, Depends(oauth2_scheme)]


def get_current_user(session: SessionDep, token: TokenDep) -> DBUser:
    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        user_id = payload.get('sub')
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired"
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
        )
    cursor = session.execute(get_user_by_id_query, (user_id,))
    user = cursor.fetchone()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    return DBUser(**dict(user))


CurrentUser = Annotated[DBUser, Depends(get_current_user)]


def get_current_admin_user(current_user: CurrentUser) -> DBUser:
    if current_user.role != Role.admin.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='The user does not have enough privileges',
        )
    return current_user


def get_user_from_refresh_token(request: Request) -> UUID:
    rt = request.cookies.get(TokenType.REFRESH_TOKEN.value)

    if not rt:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail='Missed refresh token'
        )
    payload = decode_jwt_token(rt)

    if payload.get('token_type') != TokenType.REFRESH_TOKEN.value:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid refresh token'
        )

    user_id = payload.get('sub')

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid token: no subject'
        )

    return UUID(user_id)
