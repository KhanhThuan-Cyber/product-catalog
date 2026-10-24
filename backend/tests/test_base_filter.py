from sqlalchemy import select
from sqlalchemy.dialects import postgresql

from app.models.product import Product
from app.repositories.base_filter import BaseFilter


def compile_query(stmt) -> str:
    """Helper biên dịch câu lệnh SQLAlchemy sang chuỗi SQL thô để kiểm tra cú pháp."""
    return str(
        stmt.compile(
            dialect=postgresql.dialect(),
            compile_kwargs={"literal_binds": True},
        )
    )


def test_apply_search_none_returns_same_stmt():
    stmt = select(Product)
    result = BaseFilter.apply_search(stmt, None, [Product.name])
    assert compile_query(stmt) == compile_query(result)


def test_apply_search_whitespace_returns_same_stmt():
    stmt = select(Product)
    result = BaseFilter.apply_search(stmt, "   ", [Product.name])
    assert compile_query(stmt) == compile_query(result)


def test_apply_search_valid_keyword():
    stmt = select(Product)
    result = BaseFilter.apply_search(stmt, "keyboard", [Product.name])
    sql = compile_query(result)

    assert "ILIKE" in sql or "ilike" in sql.lower()
    assert "%keyboard%" in sql


def test_apply_search_multiple_columns():
    stmt = select(Product)
    result = BaseFilter.apply_search(stmt, "pro", [Product.name, Product.description])
    sql = compile_query(result)

    assert "OR" in sql
    assert "%pro%" in sql
