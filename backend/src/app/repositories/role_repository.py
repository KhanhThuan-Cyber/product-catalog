from sqlalchemy.orm import Session

from app.models.role import Role
from app.repositories.base_repository import BaseRepository


class RoleRepository(BaseRepository[Role]):
    """Repository quản lý truy vấn dữ liệu Role kế thừa BaseRepository."""

    def __init__(self) -> None:
        super().__init__(Role)

    def get_by_name(self, db: Session, name: str) -> Role | None:
        """Lấy Role theo tên vai trò (ví dụ: 'admin', 'user')."""
        clean_name = name.strip().lower()
        return db.query(Role).filter(Role.name == clean_name).first()

    def get_by_id(self, db: Session, role_id: int) -> Role | None:
        """Lấy Role theo ID."""
        return db.query(Role).filter(Role.id == role_id).first()

    def list_all(self, db: Session) -> list[Role]:
        """Lấy danh sách tất cả các Role theo thứ tự ID."""
        return list(db.query(Role).order_by(Role.id).all())

    def create(self, db: Session, role: Role) -> Role:
        """Thêm Role mới vào session."""
        db.add(role)
        return role
