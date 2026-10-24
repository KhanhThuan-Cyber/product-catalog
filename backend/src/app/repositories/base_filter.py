from typing import Any
from sqlalchemy import ColumnElement, Select, or_


class BaseFilter:
    """Lớp trừu tượng cơ sở cung cấp các cơ chế xây dựng truy vấn SQL động theo hướng OOP.
    
    Được thiết kế để tái sử dụng cho mọi Model/Entity trong hệ thống:
    - `apply_search`: Tìm kiếm mờ không phân biệt hoa thường (ilike).
    - `apply_exact`: Lọc chính xác giá trị (equality).
    - `apply_range`: Lọc theo khoảng giá trị linh hoạt [min_val, max_val].
    - `apply_sort`: Sắp xếp an toàn dựa trên Whitelist mapping (chống SQL Injection).
    """

    @staticmethod
    def apply_search(
        stmt: Select,
        search_term: str | None,
        columns: list[ColumnElement],
    ) -> Select:
        """Áp dụng tìm kiếm không phân biệt chữ hoa/thường (ilike) trên danh sách cột."""
        if not search_term or not search_term.strip():
            return stmt

        keyword = f"%{search_term.strip()}%"
        conditions = [col.ilike(keyword) for col in columns]

        if not conditions:
            return stmt

        return stmt.where(or_(*conditions))

    @staticmethod
    def apply_exact(
        stmt: Select,
        column: ColumnElement,
        value: Any | None,
    ) -> Select:
        """Áp dụng lọc chính xác theo một giá trị (nếu value khác None)."""
        if value is not None:
            return stmt.where(column == value)
        return stmt

    @staticmethod
    def apply_range(
        stmt: Select,
        column: ColumnElement,
        min_val: Any | None = None,
        max_val: Any | None = None,
    ) -> Select:
        """Áp dụng lọc theo khoảng giá trị [min_val, max_val] (nếu có giá trị)."""
        if min_val is not None:
            stmt = stmt.where(column >= min_val)
        if max_val is not None:
            stmt = stmt.where(column <= max_val)
        return stmt

    @staticmethod
    def apply_sort(
        stmt: Select,
        sort_by: Any,
        order: Any,
        whitelist: dict[Any, ColumnElement],
        default_column: ColumnElement,
    ) -> Select:
        """Áp dụng sắp xếp an toàn theo whitelist mapping.
        
        Args:
            stmt: Câu lệnh Select của SQLAlchemy.
            sort_by: Tên trường cần sắp xếp (hoặc Enum).
            order: Chiều sắp xếp ('asc' hoặc 'desc' hoặc Enum).
            whitelist: Bảng map từ tên trường sang thuộc tính ColumnElement thực tế của Model.
            default_column: Cột sắp xếp mặc định nếu sort_by không tìm thấy.
        """
        field_key = sort_by.value if hasattr(sort_by, "value") else sort_by
        order_key = (
            order.value
            if hasattr(order, "value")
            else str(order).lower()
            if order
            else "asc"
        )

        column = whitelist.get(field_key, default_column)

        if order_key == "desc":
            return stmt.order_by(column.desc())
        return stmt.order_by(column.asc())
