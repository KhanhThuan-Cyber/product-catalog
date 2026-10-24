from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.user import User
from app.repositories.base_repository import BaseRepository


class UserRepository(BaseRepository[User]):
    """Repository quản lý truy vấn dữ liệu User kế thừa BaseRepository."""

    def __init__(self) -> None:
        super().__init__(User)

    def get_by_id(self, db: Session, user_id: int) -> User | None:
        """Lấy thông tin người dùng theo ID."""
        return db.query(User).filter(User.id == user_id).first()

    def get_by_email(self, db: Session, email: str) -> User | None:
        """Lấy thông tin người dùng theo email (không phân biệt chữ hoa/thường)."""
        clean_email = email.strip().lower()
        return db.query(User).filter(func.lower(User.email) == clean_email).first()

    def list_all(self, db: Session) -> list[User]:
        """Lấy toàn bộ danh sách người dùng trong hệ thống (sắp xếp theo ID)."""
        return list(db.query(User).order_by(User.id).all())

    def create(self, db: Session, user: User) -> User:
        """Thêm người dùng mới vào session."""
        db.add(user)
        return user

    def update_status(self, db: Session, user: User, is_active: bool) -> User:
        """Cập nhật trạng thái kích hoạt của người dùng."""
        user.is_active = is_active
        db.commit()
        db.refresh(user)
        return user

    def update_role(self, db: Session, user: User, role_id: int) -> User:
        """Cập nhật vai trò (Role) của người dùng."""
        user.role_id = role_id
        db.commit()
        db.refresh(user)
        return user
