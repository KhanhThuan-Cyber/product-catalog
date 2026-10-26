from typing import Generic, Sequence, Type, TypeVar
from sqlalchemy import Select, func, select
from sqlalchemy.orm import Session

from app.schemas.pagination import PaginationParams

ModelType = TypeVar("ModelType")


class BaseRepository(Generic[ModelType]):
    def __init__(self, model: Type[ModelType]) -> None:
        self.model = model

    def paginate(
        self,
        db: Session,
        stmt: Select,
        pagination: PaginationParams,
    ) -> tuple[Sequence[ModelType], int]:
       
        count_stmt = select(func.count()).select_from(stmt.order_by(None).subquery())
        total = db.scalar(count_stmt) or 0
        paginated_stmt = stmt.offset(pagination.offset).limit(pagination.limit)
        items = list(db.scalars(paginated_stmt).all())

        return items, total
