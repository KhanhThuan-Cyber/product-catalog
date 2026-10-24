import math
from typing import Generic, Sequence, TypeVar
from pydantic import BaseModel, ConfigDict, Field

T = TypeVar("T")


class PaginationParams(BaseModel):
    """Value Object đóng gói tham số phân trang đầu vào.
    
    Cung cấp các properties tính toán `offset` và `limit` để truyền trực tiếp
    vào câu truy vấn SQLAlchemy.
    """

    page: int = Field(
        default=1,
        ge=1,
        description="Số thứ tự trang hiện tại (bắt đầu từ 1)",
    )
    page_size: int = Field(
        default=10,
        ge=1,
        le=100,
        description="Số lượng bản ghi tối đa trên một trang (1 đến 100)",
    )

    @property
    def offset(self) -> int:
        """Vị trí bắt đầu lấy dữ liệu trong SQL offset."""
        return (self.page - 1) * self.page_size

    @property
    def limit(self) -> int:
        """Số lượng bản ghi lấy trong SQL limit."""
        return self.page_size


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic Schema định dạng phản hồi phân trang chuẩn cho toàn hệ thống.
    
    Áp dụng Factory Method Pattern `create()` để tự động đóng gói dữ liệu
    và tính toán `total_pages`.
    """

    items: Sequence[T] = Field(description="Danh sách dữ liệu bản ghi của trang hiện tại")
    total: int = Field(ge=0, description="Tổng số bản ghi thỏa mãn điều kiện")
    page: int = Field(ge=1, description="Trang hiện tại")
    page_size: int = Field(ge=1, le=100, description="Số bản ghi trên mỗi trang")
    total_pages: int = Field(ge=0, description="Tổng số trang có thể có")

    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def create(
        cls,
        items: Sequence[T],
        total: int,
        page: int | PaginationParams = 1,
        page_size: int = 10,
    ) -> "PaginatedResponse[T]":
        """Factory method tạo PaginatedResponse tự động tính toán `total_pages`.
        
        Args:
            items: Danh sách phần tử của trang hiện tại.
            total: Tổng số bản ghi thỏa mãn điều kiện lọc.
            page: Số trang hiện tại (int) hoặc đối tượng PaginationParams.
            page_size: Số phần tử trên mỗi trang (chỉ dùng khi page là int).
        """
        if isinstance(page, PaginationParams):
            current_page = page.page
            current_page_size = page.page_size
        else:
            current_page = page
            current_page_size = page_size

        total_pages = (
            math.ceil(total / current_page_size)
            if current_page_size > 0 and total > 0
            else 0
        )

        return cls(
            items=items,
            total=total,
            page=current_page,
            page_size=current_page_size,
            total_pages=total_pages,
        )
