from typing import Generic, Sequence, Type, TypeVar
from sqlalchemy import Select, func, select
from sqlalchemy.orm import Session

from app.schemas.pagination import PaginationParams

ModelType = TypeVar("ModelType")


class BaseRepository(Generic[ModelType]):
    """Lớp Repository cơ sở triển khai các thao tác truy vấn chung theo hướng OOP.
    
    Cung cấp cơ chế phân trang `paginate()` tái sử dụng cho mọi Model/Entity trong hệ thống.
    """

    def __init__(self, model: Type[ModelType]) -> None:
        self.model = model

    def paginate(
        self,
        db: Session,
        stmt: Select,
        pagination: PaginationParams,
    ) -> tuple[Sequence[ModelType], int]:
        """Thực hiện đếm tổng số bản ghi và áp dụng offset, limit để phân trang.

        Args:
            db: SQLAlchemy Session.
            stmt: Câu lệnh Select đã được áp dụng bộ lọc và sắp xếp.
            pagination: Đối tượng PaginationParams chứa page và page_size.

        Returns:
            tuple(items, total): Danh sách bản ghi trang hiện tại và tổng số bản ghi thỏa điều kiện.
        """
        # 1. Đếm tổng số bản ghi thỏa điều kiện (loại bỏ order_by để tối ưu hiệu năng đếm của DB)
        count_stmt = select(func.count()).select_from(stmt.order_by(None).subquery())
        total = db.scalar(count_stmt) or 0

        # 2. Áp dụng offset và limit từ PaginationParams
        paginated_stmt = stmt.offset(pagination.offset).limit(pagination.limit)
        items = list(db.scalars(paginated_stmt).all())

        return items, total
