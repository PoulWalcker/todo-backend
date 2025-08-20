from pydantic import BaseModel, Field


class Status(BaseModel):
    title: str = Field(..., min_length=1, max_length=100, description='Status title')


class DBStatus(Status):
    status_id: str = Field(..., description='Status ID')


class PublicStatus(Status):
    status_id: str = Field(..., description='Status ID')


class PublicStatuses(BaseModel):
    statuses: list[PublicStatus]
    count: int


class CreateStatus(Status):
    pass


class UpdateStatus(BaseModel):
    title: str | None = Field(
        default=None, min_length=1, max_length=100, description='Status title'
    )
