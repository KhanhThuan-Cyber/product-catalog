from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.schemas.pagination import PaginationParams


class BaseService:
    """Lớp nền cung cấp các tiện ích nghiệp vụ dùng chung cho tất cả Service."""

    def ensure_exists(self, obj, name: str = "Resource"):
        """Kiểm tra đối tượng tồn tại, ném 404 nếu None."""
        if obj is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"{name} not found",
            )
        return obj

    def commit_or_rollback(self, db: Session, conflict_detail: str = "Data conflict") -> None:
        """Commit transaction, rollback và ném 409 nếu có IntegrityError."""
        try:
            db.commit()
        except IntegrityError:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=conflict_detail,
            )

    def apply_update(self, obj, data, exclude_unset: bool = False) -> None:
        """Áp dụng dữ liệu từ schema Pydantic lên SQLAlchemy model object."""
        update_data = data.model_dump(exclude_unset=exclude_unset)
        for field, value in update_data.items():
            setattr(obj, field, value)
