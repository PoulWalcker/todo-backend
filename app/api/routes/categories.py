from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status

from app.crud import categories as crud_categories
from app.api.dependencies import SessionDep, get_current_admin_user, get_current_user
from app.schemas.categories import (
    UpdateCategory,
    CreateCategory,
    PublicCategory,
    PublicCategories,
)
from app.core.exceptions import DuplicateError, CreationError


router = APIRouter(prefix='/categories', tags=['categories'])


@router.get(
    '/', response_model=PublicCategories, dependencies=[Depends(get_current_user)]
)
def read_categories(session: SessionDep, offset: int = 0, limit: int = 100):
    """
    Retrieve categories.
    """
    categories = crud_categories.get_categories(session, limit, offset)
    total_categories = len(categories)

    return PublicCategories(categories=categories, count=total_categories)


@router.get(
    '/{category_id}',
    response_model=PublicCategory,
    dependencies=[Depends(get_current_user)],
)
def read_category_by_id(category_id: UUID, session: SessionDep):
    """
    Get a specific category by id.
    """
    category = crud_categories.get_category_by_id(
        category_id=category_id, connection=session
    )

    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Category not found"
        )

    return category


@router.post(
    '/', dependencies=[Depends(get_current_admin_user)], response_model=PublicCategory
)
def create_category(*, session: SessionDep, category_create: CreateCategory):
    """
    Create new category.
    """
    try:
        category = crud_categories.create_category(
            category_create=category_create, connection=session
        )

        return PublicCategory(category_id=category.category_id, title=category.title)

    except DuplicateError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=e.message)
    except CreationError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=e.message
        )


@router.patch(
    '/{category_id}',
    dependencies=[Depends(get_current_admin_user)],
    response_model=PublicCategory,
)
def update_category(
    *, category_id: UUID, category_update: UpdateCategory, session: SessionDep
):
    """
    Update category.
    """
    db_category = crud_categories.get_category_by_id(
        category_id=category_id, connection=session
    )

    if not db_category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='The category with this id does not exist in the system',
        )
    if db_category.title is not None:
        existing_category = crud_categories.get_category_by_title(
            title=category_update.title, connection=session
        )

        if existing_category and existing_category.category_id != category_id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail='Category with this title already exists',
            )

    db_category = crud_categories.update_category(
        category_id=category_id, category_update=category_update, connection=session
    )

    return db_category


@router.delete(
    '/{category_id}',
    dependencies=[Depends(get_current_admin_user)],
)
def delete_category(
    category_id: UUID,
    session: SessionDep,
) -> dict:
    """
    Delete a category.
    """
    category = crud_categories.get_category_by_id(
        category_id=category_id, connection=session
    )

    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Category not found"
        )

    is_deleted = crud_categories.delete_category(
        category_id=category_id, connection=session
    )

    if not is_deleted:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='The category with this id is not deleted.',
        )
    return {'message': 'Category deleted successfully'}
