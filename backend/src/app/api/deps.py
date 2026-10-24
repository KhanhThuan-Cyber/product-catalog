from collections.abc import Generator
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import jwt
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.core.security import decode_access_token
from app.models.user import User
from app.repositories.user_repository import UserRepository

# Cấu hình OAuth2 Bearer token extractor
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/Thuancyber/auth/login")
user_repo = UserRepository()


def get_db() -> Generator[Session, None, None]:
    """Dependency cung cấp phiên làm việc với cơ sở dữ liệu SQLAlchemy."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    """Dependency xác thực JWT Token và trích xuất User hiện tại."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token xác thực không hợp lệ hoặc đã hết hạn",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = decode_access_token(token)
        user_id_str: str | None = payload.get("sub")
        if user_id_str is None:
            raise credentials_exception
        user_id = int(user_id_str)
    except (jwt.PyJWTError, ValueError):
        raise credentials_exception

    user = user_repo.get_by_id(db, user_id)
    if user is None:
        raise credentials_exception

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tài khoản người dùng đã bị vô hiệu hóa",
        )

    return user


class RoleChecker:
    """Lớp kiểm tra phân quyền đóng gói theo hướng OOP, tái sử dụng cho mọi vai trò."""

    def __init__(self, allowed_roles: list[str]) -> None:
        self.allowed_roles = allowed_roles

    def __call__(self, current_user: User = Depends(get_current_user)) -> User:
        user_role = current_user.role.name if current_user.role else ""
        if user_role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Bạn không có quyền thực hiện hành động này",
            )
        return current_user


# Guards sẵn sàng sử dụng
require_admin = RoleChecker(["admin"])
require_authenticated = get_current_user
