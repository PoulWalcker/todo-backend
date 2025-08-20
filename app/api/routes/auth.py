from datetime import timedelta
from fastapi import APIRouter, Response, Request, HTTPException, status

from app.crud import users as crud_users
from app.api.dependencies import (
    SessionDep,
    get_user_from_refresh_token,
)
from app.schemas.users import LoginUser
from app.core.security import verify_password, create_jwt_token, TokenType
from app.core.config import settings


router = APIRouter(prefix='/auth', tags=['auth'])


@router.post('/signin')
def signin(response: Response, user_login: LoginUser, session: SessionDep):
    user = crud_users.get_user_by_email(
        email=user_login.email.lower().strip(), connection=session
    )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail='User not found'
        )

    if not verify_password(user_login.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid password or email'
        )

    access_token = create_jwt_token(
        subject=user.user_id,
        expire_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        token_type=TokenType.ACCESS_TOKEN,
    )

    refresh_token = create_jwt_token(
        subject=user.user_id,
        expire_delta=timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES),
        token_type=TokenType.REFRESH_TOKEN,
    )

    response.set_cookie(
        key=TokenType.REFRESH_TOKEN.value,
        value=refresh_token,
        httponly=True,
        max_age=settings.REFRESH_TOKEN_EXPIRE_MINUTES * 60,
        # path=f'{settings.API_V1_STR}/auth/refresh'  # ToDO Fix the problem with Path. This does not work
        path='/',
    )

    return {
        'access_token': access_token,
        'token_type': 'bearer',
    }


@router.post('/refresh')
def refresh_token(request: Request, session: SessionDep):
    user_id = get_user_from_refresh_token(request)

    db_user = crud_users.get_user_by_id(user_id, session)

    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail='User not found'
        )

    access_token = create_jwt_token(
        subject=user_id,
        expire_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        token_type=TokenType.ACCESS_TOKEN,
    )

    return {
        'access_token': access_token,
        'token_type': 'bearer',
    }


@router.post('/signout')
def logout(response: Response):
    response.delete_cookie(TokenType.REFRESH_TOKEN.value)
    return {"message": "Logged out"}
