from uuid import uuid4, UUID
from sqlite3 import Connection

from app.schemas.items import DBItem, CreateItem, UpdateItem, PublicItem

# Queries
add_item_query = (
    'INSERT INTO Items (item_id, title, description, category_id, status_id, user_id)'
    ' VALUES (?, ?, ?, ?, ?, ?) RETURNING *'
)

update_item_title_query = 'UPDATE Items SET title = ? WHERE item_id = ?'
update_item_description_query = 'UPDATE Items SET description = ? WHERE item_id = ?'
update_item_category_id_query = 'UPDATE Items SET category_id = ? WHERE item_id = ?'
update_item_status_id_query = 'UPDATE Items SET status_id = ? WHERE item_id = ?'

get_item_by_id_query = 'SELECT * FROM Items WHERE item_id = ?'
get_items_query = 'SELECT * FROM Items WHERE user_id = IFNULL(?, user_id) ORDER BY user_id ASC LIMIT ? OFFSET ?'
delete_item_query = 'DELETE FROM Items WHERE item_id = ?'


def create_item(
    user_id: UUID, item_create: CreateItem, connection: Connection
) -> DBItem | None:
    with connection:
        item_id = str(uuid4())
        cursor = connection.execute(
            add_item_query,
            (
                item_id,
                item_create.title.lower().strip(),
                item_create.description,
                str(item_create.category_id) if item_create.category_id else None,
                str(item_create.status_id) if item_create.status_id else None,
                str(user_id),
            ),
        )
        item = cursor.fetchone()
    return DBItem(**dict(item)) if item else None


def update_item(
    item_id: UUID, item_update: UpdateItem, connection: Connection
) -> DBItem | None:
    payload = item_update.model_dump(exclude_unset=True)
    if not payload:
        return None

    with connection:
        changed = False
        if item_update.title is not None:
            connection.execute(
                update_item_title_query,
                (item_update.title.lower().strip(), str(item_id)),
            )
            changed = True
        if item_update.description is not None:
            connection.execute(
                update_item_description_query, (item_update.description, str(item_id))
            )
            changed = True
        if item_update.category_id is not None:
            connection.execute(
                update_item_category_id_query, (item_update.category_id, str(item_id))
            )
            changed = True
        if item_update.status_id is not None:
            connection.execute(
                update_item_status_id_query, (item_update.status_id, str(item_id))
            )
            changed = True
        if not changed:
            return None

        cursor = connection.execute(get_item_by_id_query, (str(item_id),))
        db_item = cursor.fetchone()

    return DBItem(**dict(db_item)) if db_item else None


def delete_item(item_id: UUID, connection: Connection) -> bool:
    with connection:
        cursor = connection.execute(delete_item_query, (str(item_id),))
    return cursor.rowcount > 0


def get_item_by_id(item_id: UUID, connection: Connection) -> DBItem | None:
    cursor = connection.execute(get_item_by_id_query, (str(item_id),))
    item = cursor.fetchone()
    return DBItem(**dict(item)) if item else None


def get_items(
    connection: Connection, limit: int, offset: int, user_id: UUID | None = None
) -> list[PublicItem]:
    user_id = None if user_id is None else str(user_id)

    cursor = connection.execute(get_items_query, (user_id, limit, offset))
    items = cursor.fetchall()

    return [PublicItem(**dict(item)) for item in items]
