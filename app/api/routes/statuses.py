from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status

from app.crud import statuses as crud_statuses
from app.api.dependencies import SessionDep, get_current_admin_user, get_current_user
from app.schemas.statuses import (
    UpdateStatus,
    CreateStatus,
    PublicStatus,
    PublicStatuses,
)

from app.core.exceptions import DuplicateError, CreationError


router = APIRouter(prefix='/statuses', tags=['statuses'])


@router.get(
    '/', response_model=PublicStatuses, dependencies=[Depends(get_current_user)]
)
def read_statuses(session: SessionDep, offset: int = 0, limit: int = 100):
    """
    Retrieve statuses.
    """
    statuses = crud_statuses.get_statuses(session, limit, offset)
    total_statuses = len(statuses)

    return PublicStatuses(statuses=statuses, count=total_statuses)


@router.get(
    '/{status_id}',
    response_model=PublicStatus,
    dependencies=[Depends(get_current_user)],
)
def read_status_by_id(status_id: UUID, session: SessionDep):
    """
    Get a specific status by id.
    """
    status_item = crud_statuses.get_status_by_id(status_id, session)

    if not status_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Status not found"
        )

    return status_item


@router.post(
    '/', dependencies=[Depends(get_current_admin_user)], response_model=PublicStatus
)
def create_status(*, session: SessionDep, status_create: CreateStatus):
    """
    Create new status.
    """
    try:
        status_item = crud_statuses.create_status(status_create, session)
        return PublicStatus(status_id=status_item.status_id, title=status_item.title)

    except DuplicateError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=e.message)
    except CreationError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=e.message
        )


@router.patch(
    '/{status_id}',
    dependencies=[Depends(get_current_admin_user)],
    response_model=PublicStatus,
)
def update_status(*, status_id: UUID, status_update: UpdateStatus, session: SessionDep):
    """
    Update status.
    """
    db_status = crud_statuses.get_status_by_id(status_id, session)
    if not db_status:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='The status with this id does not exist in the system',
        )
    if db_status.title is not None:
        existing_status = crud_statuses.get_status_by_title(
            status_update.title, session
        )

        if existing_status and existing_status.status_id != status_id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail='Status with this title already exists',
            )

    db_status = crud_statuses.update_status(status_id, status_update, session)
    return db_status


@router.delete(
    '/{status_id}',
    dependencies=[Depends(get_current_admin_user)],
)
def delete_status(
    status_id: UUID,
    session: SessionDep,
) -> dict:
    """
    Delete a status.
    """
    status_item = crud_statuses.get_status_by_id(status_id, session)
    if not status_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Status not found"
        )

    is_deleted = crud_statuses.delete_status(status_id, session)
    if not is_deleted:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='The status with this id is not deleted.',
        )
    return {'message': 'Status deleted successfully'}
