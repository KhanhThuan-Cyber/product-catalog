from typing import Generic, Sequence, TypeVar
from pydantic import BaseModel, ConfigDict, Field

T = TypeVar("T")


class PaginationParams(BaseModel):
    """Tham số phân trang đầu vào cho truy vấn."""

    page: int = Field(
        default=1, ge=1, description="Số thứ tự trang hiện tại (bắt đầu từ 1)"
    )
    page_size: int = Field(
        default=10, ge=1, le=100, description="Số bản ghi tối đa trên một trang"
    )

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.page_size

    @property
    def limit(self) -> int:
        return self.page_size


class PaginatedResponse(BaseModel, Generic[T]):

    items: Sequence[T] = Field(description="Danh sách dữ liệu trang hiện tại")
    total: int = Field(ge=0, description="Tổng số bản ghi thỏa điều kiện")
    page: int = Field(ge=1, description="Trang hiện tại")
    page_size: int = Field(ge=1, le=100, description="Số bản ghi trên mỗi trang")
    total_pages: int = Field(ge=0, description="Tổng số trang có thể có")

    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def create(
        cls,
        items: Sequence[T],
        total: int,
        pagination: PaginationParams,
    ) -> "PaginatedResponse[T]":
        total_pages = (
            (total + pagination.page_size - 1) // pagination.page_size
            if pagination.page_size > 0 and total > 0
            else 0
        )
        return cls(
            items=items,
            total=total,
            page=pagination.page,
            page_size=pagination.page_size,
            total_pages=total_pages,
        )