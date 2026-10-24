from decimal import Decimal
import pytest
from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.dialects import postgresql

from app.models.product import Product
from app.repositories.base_filter import BaseFilter
from app.schemas.product_filter import ProductFilter


def compile_query(stmt) -> str:
    """Helper biên dịch câu lệnh SQLAlchemy sang chuỗi SQL thô."""
    return str(
        stmt.compile(
            dialect=postgresql.dialect(),
            compile_kwargs={"literal_binds": True},
        )
    )


def test_base_filter_apply_exact():
    stmt = select(Product)
    # None value -> không thêm điều kiện
    unchanged = BaseFilter.apply_exact(stmt, Product.category_id, None)
    assert compile_query(stmt) == compile_query(unchanged)

    # Có giá trị -> thêm điều kiện bằng
    filtered = BaseFilter.apply_exact(stmt, Product.category_id, 3)
    sql = compile_query(filtered)
    assert "products.category_id = 3" in sql


def test_base_filter_apply_range():
    stmt = select(Product)

    # Chỉ có min_val
    stmt_min = BaseFilter.apply_range(stmt, Product.price, min_val=Decimal("100"))
    assert "products.price >= 100" in compile_query(stmt_min)

    # Chỉ có max_val
    stmt_max = BaseFilter.apply_range(stmt, Product.price, max_val=Decimal("500"))
    assert "products.price <= 500" in compile_query(stmt_max)

    # Có cả hai
    stmt_both = BaseFilter.apply_range(
        stmt, Product.price, min_val=Decimal("100"), max_val=Decimal("500")
    )
    sql = compile_query(stmt_both)
    assert "products.price >= 100" in sql
    assert "products.price <= 500" in sql


def test_product_filter_price_validation():
    # Hợp lệ: min_price <= max_price
    pf = ProductFilter(min_price=Decimal("100"), max_price=Decimal("200"))
    assert pf.min_price == Decimal("100")
    assert pf.max_price == Decimal("200")

    # Bất hợp lệ: min_price > max_price
    with pytest.raises(ValidationError) as exc_info:
        ProductFilter(min_price=Decimal("300"), max_price=Decimal("200"))
    assert "min_price không được lớn hơn max_price" in str(exc_info.value)


def test_product_filter_combined_query():
    pf = ProductFilter(
        search="keyboard",
        category_id=2,
        min_price=Decimal("50000"),
        max_price=Decimal("200000"),
    )

    stmt = select(Product)
    result = pf.apply(stmt)
    sql = compile_query(result)

    assert "ILIKE" in sql or "ilike" in sql.lower()
    assert "%keyboard%" in sql
    assert "products.category_id = 2" in sql
    assert "products.price >= 50000" in sql
    assert "products.price <= 200000" in sql
