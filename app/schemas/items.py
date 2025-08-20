from uuid import UUID
from pydantic import BaseModel, Field
from datetime import datetime


class Item(BaseModel):
    title: str = Field(
        ..., min_length=1, max_length=150, description="Human-readable item title"
    )
    description: str = Field(
        None, min_length=1, max_length=1000, description="Detailed item description"
    )
    category_id: UUID | None = Field(
        None, description="Category ID (UUID, FK to Categories)"
    )
    status_id: UUID | None = Field(None, description="Status ID (UUID, FK to Statuses)")


class CreateItem(Item):
    pass


class PublicItem(Item):
    item_id: UUID = Field(..., description="Item ID (UUID)")
    user_id: UUID = Field(..., description="Owner user ID (UUID)")


class PublicItems(BaseModel):
    items: list[PublicItem] = Field(default_factory=list, description="List of items")
    count: int = Field(..., ge=0, description="Number of items")


class DBItem(Item):
    item_id: UUID = Field(..., description="Item ID (UUID)")
    user_id: UUID = Field(..., description="Owner user ID (UUID)")
    created_at: datetime = Field(..., description="Creation timestamp (UTC)")
    updated_at: datetime = Field(..., description="Last update timestamp (UTC)")


class UpdateItem(BaseModel):
    title: str | None = Field(None, description="New title")
    description: str | None = Field(None, description="New description")
    category_id: UUID | None = Field(None, description="New category ID (UUID)")
    status_id: UUID | None = Field(None, description="New status ID (UUID)")
