from pydantic import BaseModel, Field


class Category(BaseModel):
    title: str = Field(..., min_length=1, max_length=100, description='Category title')


class DBCategory(Category):
    category_id: str = Field(..., description='Category ID')


class PublicCategory(Category):
    category_id: str = Field(..., description='Category ID')


class PublicCategories(BaseModel):
    categories: list[PublicCategory]
    count: int


class CreateCategory(Category):
    pass


class UpdateCategory(BaseModel):
    title: str | None = Field(
        default=None, min_length=1, max_length=100, description='Category title'
    )
