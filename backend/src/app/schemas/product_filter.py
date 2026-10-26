from decimal import Decimal
from typing import Any
from pydantic import BaseModel, Field, model_validator
from sqlalchemy import ColumnElement, Select

from app.models.product import Product
from app.repositories.base_filter import BaseFilter
from app.schemas.sorting import ProductSortBy, SortOrder

PRODUCT_SORT_WHITELIST: dict[str, ColumnElement] = {
    ProductSortBy.id.value: Product.id,
    ProductSortBy.price.value: Product.price,
    ProductSortBy.created_at.value: Product.created_at,
    ProductSortBy.name.value: Product.name,
}

class ProductFilter(BaseModel):
    """Value Object đóng gói các tiêu chí tìm kiếm, lọc và sắp xếp cho Product.
    
    Tự động xác thực nghiệp vụ (ví dụ: min_price <= max_price),
    giới hạn các trường sắp xếp an toàn qua Whitelist,
    và đóng gói logic áp dụng điều kiện lên câu lệnh SQLAlchemy Select.
    """

    search: str | None = Field(
        default=None,
        max_length=100,
        description="Từ khóa tìm kiếm theo tên sản phẩm (không phân biệt chữ hoa/thường)",
    )
    category_id: int | None = Field(
        default=None,
        gt=0,
        description="Lọc theo mã danh mục sản phẩm (category_id > 0)",
    )
    min_price: Decimal | None = Field(
        default=None,
        ge=0,
        description="Giá sản phẩm thấp nhất (>= 0)",
    )
    max_price: Decimal | None = Field(
        default=None,
        ge=0,
        description="Giá sản phẩm cao nhất (>= 0)",
    )
    sort_by: ProductSortBy = Field(
        default=ProductSortBy.id,
        description="Trường cần sắp xếp (id, price, created_at, name)",
    )
    order: SortOrder = Field(
        default=SortOrder.asc,
        description="Chiều sắp xếp: asc (tăng dần) hoặc desc (giảm dần)",
    )

    @model_validator(mode="after")
    def validate_price_range(self) -> "ProductFilter":
        """Xác thực khoảng giá: min_price không được lớn hơn max_price."""
        if (
            self.min_price is not None
            and self.max_price is not None
            and self.min_price > self.max_price
        ):
            raise ValueError("min_price không được lớn hơn max_price")
        return self

    def apply(self, stmt: Select) -> Select:
        """Áp dụng tìm kiếm, lọc và sắp xếp an toàn lên câu lệnh SQLAlchemy Select."""
        stmt = BaseFilter.apply_search(stmt, self.search, [Product.name])
        stmt = BaseFilter.apply_exact(stmt, Product.category_id, self.category_id)
        stmt = BaseFilter.apply_range(stmt, Product.price, self.min_price, self.max_price)
        stmt = BaseFilter.apply_sort(
            stmt,
            sort_by=self.sort_by,
            order=self.order,
            whitelist=PRODUCT_SORT_WHITELIST,
            default_column=Product.id,
        )
        return stmt
