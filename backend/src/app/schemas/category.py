from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class CategoryCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    description: str | None = None


class CategoryUpdate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    description: str | None = None


class CategoryResponse(BaseModel):
    id: int
    name: str
    description: str | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
