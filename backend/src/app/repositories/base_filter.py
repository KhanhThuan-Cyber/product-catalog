import re
from typing import Any, Sequence
from sqlalchemy import ColumnElement, Select, or_


class BaseFilter:
    """Bộ công cụ hỗ trợ xây dựng truy vấn lọc và sắp xếp động cho SQLAlchemy 2.0."""

    @staticmethod
    def _escape_like_term(term: str) -> str:
        """Escape ký tự đặc biệt % và _ để tránh lỗi wildcard ngoài ý muốn."""
        return re.sub(r"([%_])", r"\\\1", term)

    @staticmethod
    def apply_search(
        stmt: Select[Any],
        search_term: str | None,
        columns: Sequence[ColumnElement[Any]],
    ) -> Select[Any]:
        """Tìm kiếm ilike an toàn trên danh sách cột."""
        if not search_term or not search_term.strip() or not columns:
            return stmt

        clean_term = BaseFilter._escape_like_term(search_term.strip())
        keyword = f"%{clean_term}%"
        conditions = [col.ilike(keyword) for col in columns]

        return stmt.where(or_(*conditions))

    @staticmethod
    def apply_exact(
        stmt: Select[Any],
        column: ColumnElement[Any],
        value: Any | None,
    ) -> Select[Any]:
        """Lọc chính xác theo giá trị nếu value khác None."""
        if value is None:
            return stmt
        return stmt.where(column == value)

    @staticmethod
    def apply_range(
        stmt: Select[Any],
        column: ColumnElement[Any],
        min_val: Any | None = None,
        max_val: Any | None = None,
    ) -> Select[Any]:
        """Lọc theo khoảng [min_val, max_val]."""
        if min_val is not None:
            stmt = stmt.where(column >= min_val)
        if max_val is not None:
            stmt = stmt.where(column <= max_val)
        return stmt

    @staticmethod
    def apply_sort(
        stmt: Select[Any],
        sort_by: Any,
        order: Any,
        whitelist: dict[Any, ColumnElement[Any]],
        default_column: ColumnElement[Any],
    ) -> Select[Any]:
        """Sắp xếp an toàn dựa trên Whitelist mapping chống SQL Injection."""
        field_key = sort_by.value if hasattr(sort_by, "value") else sort_by
        order_key = (
            order.value
            if hasattr(order, "value")
            else (str(order).lower() if order is not None else "asc")
        )

        if order_key not in {"asc", "desc"}:
            raise ValueError(f"Tham số order không hợp lệ: '{order}'. Chỉ chấp nhận 'asc' hoặc 'desc'.")

        column = whitelist.get(field_key, default_column)

        if order_key == "desc":
            return stmt.order_by(column.desc())
        return stmt.order_by(column.asc())