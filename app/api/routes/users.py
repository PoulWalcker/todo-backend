from uuid import UUID
from datetime import timedelta
from fastapi import APIRouter, Response, Depends, HTTPException, status

from app.crud import users as crud_users
from app.api.dependencies import (
    CurrentUser,
    SessionDep,
    get_current_admin_user,
    get_current_user,
)
from app.schemas.users import PublicUsers, PublicUser, CreateUser, UpdateUser, Role

from app.core.exceptions import DuplicateError, CreationError
from app.core.security import create_jwt_token, TokenType
from app.core.config import settings

router = APIRouter(prefix='/users', tags=['users'])


@router.get(
    '/', dependencies=[Depends(get_current_admin_user)], response_model=PublicUsers
)
def read_users(session: SessionDep, offset: int = 0, limit: int = 100):
    """
    Retrieve users.
    """
    users = crud_users.get_users(connection=session, limit=limit, offset=offset)

    total_users = len(users)

    return PublicUsers(users=users, count=total_users)


@router.get('/me', response_model=PublicUser)
def read_user_me(current_user: CurrentUser):
    """
    Get current user.
    """
    return current_user


@router.get('/{user_id}', response_model=PublicUser)
def read_user_by_id(user_id: UUID, session: SessionDep, current_user: CurrentUser):
    """
    Get a specific user by id.
    """
    user = crud_users.get_user_by_id(user_id=user_id, connection=session)

    if user == current_user:
        return user
    if current_user.role != Role.admin.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='The user does not have enough privileges',
        )
    return user


@router.post(
    '/', dependencies=[Depends(get_current_admin_user)], response_model=PublicUser
)
def create_user(*, session: SessionDep, user_in: CreateUser):
    """
    Create new user (role defaults to 'user').
    """
    user = crud_users.get_user_by_email(user_in.email, session)

    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The user with this email already exists in the system.",
        )
    try:
        user = crud_users.create_user(user_create=user_in, connection=session)

        return user

    except DuplicateError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=e.message)
    except CreationError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=e.message
        )


@router.post('/signup')
def register_user(response: Response, session: SessionDep, user_in: CreateUser):
    """
    Create new user without the need to be logged in.
    """
    user = crud_users.get_user_by_email(email=user_in.email, connection=session)

    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The user with this email already exists in the system.",
        )

    new_user = crud_users.create_user(user_create=user_in, connection=session)

    access_token = create_jwt_token(
        subject=new_user.user_id,
        expire_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        token_type=TokenType.ACCESS_TOKEN,
    )

    refresh_token = create_jwt_token(
        subject=new_user.user_id,
        expire_delta=timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES),
        token_type=TokenType.REFRESH_TOKEN,
    )

    response.set_cookie(
        key=TokenType.REFRESH_TOKEN.value,
        value=refresh_token,
        httponly=True,
        max_age=settings.REFRESH_TOKEN_EXPIRE_MINUTES * 60,
        path='/auth/refresh',
    )

    return {
        'access_token': access_token,
        'token_type': 'bearer',
        'user': new_user.user_id,
    }


@router.patch('/me', response_model=PublicUser)
def update_user_me(
    *, session: SessionDep, user_update: UpdateUser, current_user: CurrentUser
):
    """
    Update own user.
    """

    if user_update.email:
        user = crud_users.get_user_by_email(email=user_update.email, connection=session)

        if user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="The user with this email already exists in the system.",
            )

    updated_user = crud_users.update_user(
        user_id=current_user.user_id, user_update=user_update, connection=session
    )

    return updated_user


@router.patch(
    '/{user_id}',
    dependencies=[Depends(get_current_admin_user)],
    response_model=PublicUser,
)
def update_user(*, user_id: UUID, user_update: UpdateUser, session: SessionDep):
    """
    Update a user.
    """
    db_user = crud_users.get_user_by_id(user_id=user_id, connection=session)

    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='The user with this id does not exist in the system',
        )

    if db_user.email:
        existing_user = crud_users.get_user_by_email(user_update.email, session)
        if existing_user and existing_user.id != user_id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail='User with this email already exists',
            )

    updated_user = crud_users.update_user(
        user_id=user_id, user_update=user_update, connection=session
    )

    return updated_user


@router.delete(
    '/{user_id}',
    dependencies=[Depends(get_current_admin_user)],
)
def delete_user(user_id: UUID, session: SessionDep, current_user: CurrentUser) -> dict:
    """
    Delete a user.
    """
    user = crud_users.get_user_by_id(user_id=user_id, connection=session)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    if user == current_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Super users are not allowed to delete themselves",
        )

    is_deleted = crud_users.delete_user(user_id=user_id, connection=session)

    if not is_deleted:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='The user with this id is not deleted.',
        )

    return {'message': 'User deleted successfully'}
