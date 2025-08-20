# ToDo API MVP

Minimal REST API for a personal task list.

## Stack
* Python 3.11
* FastAPI
* Pydantic
* SQLite

## Features
* CRUD for categories, statuses, and items
* Sign in at `/api/v1/auth/signin` returns an access token of type bearer
* Refresh at `/api/v1/auth/refresh` sets a new access token
* Database schema is created at startup and can run many times safely

## Project setup

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Create an environment file
Create a file named `.env` in the project root.

```
PROJECT_NAME=ToDo API
API_V1_STR=/api/v1
DATABASE_PATH=/data/app.db
ADMIN_EMAIL=admin@example.com
ADMIN_PASSWORD=changeme
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_MINUTES=43200
```

### 3. Run in development
```bash
fastapi dev app/main.py
```
Open docs at http://localhost:8000/docs

## Docker

### Build and start
```bash
docker compose build
docker compose up
```

SQLite data is stored in the named volume `app_data` so it persists across restarts.

## API overview
Base prefix: `/api/v1`

Auth
* `POST /auth/signin` accepts form data with fields `username` and `password` or JSON with `email` and `password` depending on configuration
* `POST /auth/refresh` reads the refresh token from cookie and returns a new access token
* `POST /auth/signout` clears the refresh token cookie

Core
* `GET /users` and other user routes
* `GET /items` and item routes
* `GET /categories` and category routes
* `GET /statuses` and status routes

## Notes
* Initialization uses `CREATE TABLE IF NOT EXISTS` and inserts with `ON CONFLICT DO NOTHING`
* You can switch to a versioned schema using `PRAGMA user_version` for future migrations
* The refresh token is stored in an HTTP only cookie
