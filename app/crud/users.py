from uuid import uuid4, UUID
from sqlite3 import Connection, IntegrityError

from app.schemas.users import DBUser, CreateUser, UpdateUser, Role, PublicUser
from app.core.security import hash_password
from app.core.exceptions import DuplicateError, CreationError

# Queries
add_user_query = (
    'INSERT INTO Users (user_id, first_name, last_name, email, hashed_password, role)'
    ' VALUES (?, ?, ?, ?, ?, ?) RETURNING *'
)

update_user_first_name_query = 'UPDATE Users SET first_name = ? WHERE user_id = ?'
update_user_last_name_query = 'UPDATE Users SET last_name = ? WHERE user_id = ?'
update_user_email_query = 'UPDATE Users SET email = ? WHERE user_id = ?'
update_user_hashed_password_query = (
    'UPDATE Users SET hashed_password = ? WHERE user_id = ?'
)

get_user_by_id_query = 'SELECT * FROM Users WHERE user_id = ?'
get_users_query = 'SELECT * FROM Users ORDER BY user_id ASC LIMIT ? OFFSET ?'
get_user_by_email_query = 'SELECT * FROM Users WHERE email = ?'
delete_user_query = 'DELETE FROM Users WHERE user_id = ?'


def create_user(
    user_create: CreateUser, connection: Connection, role: Role = Role.user
) -> DBUser | None:
    user_id = str(uuid4())
    hashed_password = hash_password(user_create.password)

    try:
        with connection:
            cursor = connection.execute(
                add_user_query,
                (
                    user_id,
                    user_create.first_name,
                    user_create.last_name,
                    user_create.email.strip().lower(),
                    hashed_password,
                    role.value,
                ),
            )
            user = cursor.fetchone()

            if not user:
                raise CreationError(f'User not found after creating: {user_id}')
            return DBUser(**dict(user))
    except IntegrityError as e:
        # Email has UNIQUE type in Data Base
        if "Users.email" in str(e):
            raise DuplicateError("Email already exists") from e
        raise


def update_user(
    user_id: UUID, user_update: UpdateUser, connection: Connection
) -> DBUser | None:
    payload = user_update.model_dump(exclude_unset=True)
    if not payload:
        return None

    with connection:
        changed = False
        if user_update.first_name is not None:
            connection.execute(
                update_user_first_name_query, (user_update.first_name, str(user_id))
            )
            changed = True
        if user_update.last_name is not None:
            connection.execute(
                update_user_last_name_query, (user_update.last_name, str(user_id))
            )
            changed = True
        if user_update.email is not None:
            connection.execute(
                update_user_email_query,
                (user_update.email.strip().lower(), str(user_id)),
            )
            changed = True
        if user_update.password is not None:
            hashed_password = hash_password(user_update.password)
            connection.execute(
                update_user_hashed_password_query, (hashed_password, str(user_id))
            )
            changed = True
        if not changed:
            return None

        cursor = connection.execute(get_user_by_id_query, (str(user_id),))
        db_user = cursor.fetchone()

    return DBUser(**dict(db_user)) if db_user else None


def delete_user(user_id: UUID, connection: Connection) -> bool:
    with connection:
        cursor = connection.execute(delete_user_query, (str(user_id),))
    return cursor.rowcount > 0


def get_user_by_id(user_id: UUID, connection: Connection) -> DBUser | None:
    cursor = connection.execute(get_user_by_id_query, (str(user_id),))
    user = cursor.fetchone()
    return DBUser(**dict(user)) if user else None


def get_user_by_email(email: str, connection: Connection) -> DBUser | None:
    cursor = connection.execute(get_user_by_email_query, (email.strip().lower(),))
    user = cursor.fetchone()
    return DBUser(**dict(user)) if user else None


def get_users(connection: Connection, limit: int, offset: int) -> list[PublicUser]:
    cursor = connection.execute(get_users_query, (limit, offset))
    users = cursor.fetchall()

    return [PublicUser(**dict(user)) for user in users]
