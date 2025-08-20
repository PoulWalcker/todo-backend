from uuid import uuid4, UUID
from sqlite3 import Connection, IntegrityError

from app.schemas.categories import (
    DBCategory,
    CreateCategory,
    UpdateCategory,
    PublicCategory,
)
from app.core.exceptions import DuplicateError, CreationError

# Queries
add_category_query = (
    'INSERT INTO Categories (category_id, title) VALUES (?, ?) RETURNING *'
)
update_category_title_query = (
    'UPDATE Categories SET title = ? WHERE category_id = ? RETURNING *'
)
get_category_by_id_query = 'SELECT * FROM Categories WHERE category_id = ?'
get_categories_query = (
    'SELECT * FROM Categories ORDER BY category_id ASC LIMIT ? OFFSET ?'
)
get_category_by_title_query = 'SELECT * FROM Categories WHERE title = ?'
delete_category_query = 'DELETE FROM Categories WHERE category_id = ?'


def create_category(
    category_create: CreateCategory, connection: Connection
) -> DBCategory | None:
    try:
        with connection:
            category_id = str(uuid4())
            cursor = connection.execute(
                add_category_query,
                (
                    category_id,
                    category_create.title.lower().strip(),
                ),
            )
            category = cursor.fetchone()

            if not category:
                raise CreationError(f'Category not found after creating: {category_id}')
            return DBCategory(**dict(category))
    except IntegrityError as e:
        # Title has UNIQUE type in Data Base
        if "Categories.title" in str(e):
            raise DuplicateError("Category with this title already exists") from e
        raise


def update_category(
    category_id: UUID, category_update: UpdateCategory, connection: Connection
) -> DBCategory | None:
    with connection:
        cursor = connection.execute(
            update_category_title_query,
            (
                category_update.title.lower().strip(),
                str(category_id),
            ),
        )
        category = cursor.fetchone()
    return DBCategory(**dict(category)) if category else None


def delete_category(category_id: UUID, connection: Connection) -> bool:
    with connection:
        cursor = connection.execute(delete_category_query, (str(category_id),))
    return cursor.rowcount > 0


def get_category_by_id(category_id: UUID, connection: Connection) -> DBCategory | None:
    cursor = connection.execute(get_category_by_id_query, (str(category_id),))
    category = cursor.fetchone()
    return DBCategory(**dict(category)) if category else None


def get_category_by_title(title: str, connection: Connection) -> DBCategory | None:
    cursor = connection.execute(get_category_by_title_query, (title.lower().strip(),))
    category = cursor.fetchone()
    return DBCategory(**dict(category)) if category else None


def get_categories(
    connection: Connection, limit: int, offset: int
) -> list[PublicCategory]:
    cursor = connection.execute(get_categories_query, (limit, offset))
    categories = cursor.fetchall()

    return [PublicCategory(**dict(category)) for category in categories]
