from uuid import UUID
from fastapi import APIRouter, HTTPException, status

from app.crud import items as crud_items
from app.api.dependencies import (
    CurrentUser,
    SessionDep,
)
from app.schemas.items import (
    UpdateItem,
    PublicItem,
    PublicItems,
    CreateItem,
)
from app.schemas.users import Role
from app.core.exceptions import CreationError

router = APIRouter(prefix='/items', tags=['items'])


@router.get('/', response_model=PublicItems)
def read_items(
    session: SessionDep, current_user: CurrentUser, offset: int = 0, limit: int = 100
):
    """
    Retrieve to-do items.
    """

    if current_user.role == Role.admin.value:
        items = crud_items.get_items(
            connection=session, limit=limit, offset=offset, user_id=None
        )
    else:
        items = crud_items.get_items(
            connection=session, limit=limit, offset=offset, user_id=current_user.user_id
        )

    total_items = len(items)

    return PublicItems(items=items, count=total_items)


@router.get('/{item_id}', response_model=PublicItem)
def read_item_by_id(item_id: UUID, session: SessionDep, current_user: CurrentUser):
    """
    Get a specific item by id.
    """
    item = crud_items.get_item_by_id(item_id=item_id, connection=session)

    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Item not found"
        )
    if not current_user.role == Role.admin.value and (item.user_id != current_user.id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Not enough permissions"
        )

    return item


@router.post('/', response_model=PublicItem)
def create_item(*, session: SessionDep, current_user: CurrentUser, item_in: CreateItem):
    """
    Create new item.
    """
    try:
        item = crud_items.create_item(
            user_id=current_user.user_id, item_create=item_in, connection=session
        )
        return item

    except CreationError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=e.message
        )


@router.patch('/{item_id}', response_model=PublicItem)
def update_item(
    *,
    item_id: UUID,
    item_update: UpdateItem,
    session: SessionDep,
    current_user: CurrentUser,
):
    """
    Update item.
    """
    db_item = crud_items.get_item_by_id(item_id, session)
    if not db_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='The item with this id does not exist in the system',
        )

    if current_user.role != Role.admin.value and (
        current_user.user_id != db_item.user_id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions"
        )

    updated_item = crud_items.update_item(
        item_id=item_id, item_update=item_update, connection=session
    )

    return updated_item


@router.delete(
    '/{item_id}',
)
def delete_user(item_id: UUID, session: SessionDep, current_user: CurrentUser) -> dict:
    """
    Delete item.
    """
    item = crud_items.get_item_by_id(item_id, session)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Item not found"
        )
    if current_user.role != Role.admin.value and (current_user.user_id != item.user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions"
        )

    is_deleted = crud_items.delete_item(item_id=item_id, connection=session)

    if not is_deleted:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='The item with this id is not deleted.',
        )
    return {'message': 'Item deleted successfully'}
