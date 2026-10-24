import pytest
from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.dialects import postgresql

from app.models.product import Product
from app.schemas.product_filter import ProductFilter
from app.schemas.sorting import ProductSortBy, SortOrder


def compile_query(stmt) -> str:
    """Helper biên dịch câu lệnh SQLAlchemy sang chuỗi SQL thô."""
    return str(
        stmt.compile(
            dialect=postgresql.dialect(),
            compile_kwargs={"literal_binds": True},
        )
    )


def test_sort_by_price_asc_and_desc():
    # Price ASC
    pf_asc = ProductFilter(sort_by=ProductSortBy.price, order=SortOrder.asc)
    sql_asc = compile_query(pf_asc.apply(select(Product)))
    assert "ORDER BY products.price ASC" in sql_asc

    # Price DESC
    pf_desc = ProductFilter(sort_by=ProductSortBy.price, order=SortOrder.desc)
    sql_desc = compile_query(pf_desc.apply(select(Product)))
    assert "ORDER BY products.price DESC" in sql_desc


def test_sort_by_created_at_maps_to_create_at_column():
    # Kiểm tra created_at map chính xác sang cột cơ sở dữ liệu products.create_at
    pf_asc = ProductFilter(sort_by=ProductSortBy.created_at, order=SortOrder.asc)
    sql_asc = compile_query(pf_asc.apply(select(Product)))
    assert "ORDER BY products.create_at ASC" in sql_asc

    pf_desc = ProductFilter(sort_by=ProductSortBy.created_at, order=SortOrder.desc)
    sql_desc = compile_query(pf_desc.apply(select(Product)))
    assert "ORDER BY products.create_at DESC" in sql_desc


def test_sort_by_name_and_id():
    pf_name = ProductFilter(sort_by=ProductSortBy.name, order=SortOrder.asc)
    assert "ORDER BY products.name ASC" in compile_query(pf_name.apply(select(Product)))

    pf_id = ProductFilter(sort_by=ProductSortBy.id, order=SortOrder.desc)
    assert "ORDER BY products.id DESC" in compile_query(pf_id.apply(select(Product)))


def test_invalid_sort_by_rejected_by_whitelist():
    # Trường không nằm trong whitelist bị Pydantic ValidationError chặn ngay
    with pytest.raises(ValidationError):
        ProductFilter(sort_by="password")  # type: ignore

    with pytest.raises(ValidationError):
        ProductFilter(sort_by="; DROP TABLE products; --")  # type: ignore


def test_invalid_sort_order_rejected():
    with pytest.raises(ValidationError):
        ProductFilter(order="invalid_order")  # type: ignore
