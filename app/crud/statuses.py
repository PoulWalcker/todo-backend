from uuid import uuid4, UUID
from sqlite3 import Connection, IntegrityError

from app.schemas.statuses import DBStatus, CreateStatus, UpdateStatus, PublicStatus
from app.core.exceptions import CreationError, DuplicateError

# Queries
add_status_query = 'INSERT INTO Statuses (status_id, title) VALUES (?, ?) RETURNING *'
update_status_title_query = (
    'UPDATE Statuses SET title = ? WHERE status_id = ? RETURNING *'
)
get_status_by_id_query = 'SELECT * FROM Statuses WHERE status_id = ?'
get_statuses_query = 'SELECT * FROM Statuses ORDER BY status_id ASC LIMIT ? OFFSET ?'
get_status_by_title_query = 'SELECT * FROM Statuses WHERE title = ?'
delete_status_query = 'DELETE FROM Statuses WHERE status_id = ?'


def create_status(
    status_create: CreateStatus, connection: Connection
) -> DBStatus | None:
    try:
        with connection:
            status_id = str(uuid4())
            cursor = connection.execute(
                add_status_query,
                (
                    status_id,
                    status_create.title.lower().strip(),
                ),
            )
            status = cursor.fetchone()
        if not status:
            raise CreationError(f'Status not found after creating: {status_id}')

        return DBStatus(**dict(status)) if status else None
    except IntegrityError as e:
        # Title has UNIQUE type in Data Base
        if "Statuses.title" in str(e):
            raise DuplicateError("Status already exists") from e
        raise


def update_status(
    status_id: UUID, status_update: UpdateStatus, connection: Connection
) -> DBStatus | None:
    with connection:
        cursor = connection.execute(
            update_status_title_query,
            (
                status_update.title.lower().strip(),
                str(status_id),
            ),
        )
        status = cursor.fetchone()
    return DBStatus(**dict(status)) if status else None


def delete_status(status_id: UUID, connection: Connection) -> bool:
    with connection:
        cursor = connection.execute(delete_status_query, (str(status_id),))
    return cursor.rowcount > 0


def get_status_by_id(status_id: UUID, connection: Connection) -> DBStatus | None:
    cursor = connection.execute(get_status_by_id_query, (str(status_id),))
    status = cursor.fetchone()
    return DBStatus(**dict(status)) if status else None


def get_status_by_title(title: str, connection: Connection) -> DBStatus | None:
    cursor = connection.execute(get_status_by_title_query, (title.lower().strip(),))
    status = cursor.fetchone()
    return DBStatus(**dict(status)) if status else None


def get_statuses(connection: Connection, limit: int, offset: int) -> list[PublicStatus]:
    cursor = connection.execute(get_statuses_query, (limit, offset))
    statuses = cursor.fetchall()

    return [PublicStatus(**dict(status)) for status in statuses]
