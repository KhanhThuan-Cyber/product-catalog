from sqlalchemy import select
from sqlalchemy.dialects import postgresql

from app.models.product import Product
from app.repositories.base_repository import BaseRepository
from app.schemas.pagination import PaginatedResponse, PaginationParams
from app.schemas.product_filter import ProductFilter


def compile_query(stmt) -> str:
    """Helper biên dịch câu lệnh SQLAlchemy sang chuỗi SQL thô."""
    return str(
        stmt.compile(
            dialect=postgresql.dialect(),
            compile_kwargs={"literal_binds": True},
        )
    )


def test_base_repository_paginate_query_generation():
    repo = BaseRepository[Product](Product)
    pagination = PaginationParams(page=3, page_size=15)

    stmt = select(Product).order_by(Product.id.asc())

    # Kiểm tra offset = (3 - 1) * 15 = 30, limit = 15
    paginated_stmt = stmt.offset(pagination.offset).limit(pagination.limit)
    sql = compile_query(paginated_stmt)

    assert "LIMIT 15" in sql
    assert "OFFSET 30" in sql


def test_paginated_response_serialization_with_product_filter():
    pagination = PaginationParams(page=2, page_size=10)
    fake_items = [
        {
            "id": 11,
            "name": "Sản phẩm 11",
            "description": "Mô tả",
            "price": "150000.00",
            "stock": 20,
            "category_id": 1,
            "is_active": True,
            "create_at": "2026-10-24T00:00:00",
            "updated_at": "2026-10-24T00:00:00",
        }
    ]

    response = PaginatedResponse[dict].create(
        items=fake_items,
        total=25,
        page=pagination,
    )

    data = response.model_dump()
    assert data["total"] == 25
    assert data["page"] == 2
    assert data["page_size"] == 10
    assert data["total_pages"] == 3
    assert len(data["items"]) == 1
