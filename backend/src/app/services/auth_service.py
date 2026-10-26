import logging
from datetime import datetime, timezone
from typing import Any
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import (
    create_access_token,
    decode_access_token,
    get_password_hash,
    verify_password,
)
from app.models.user import User
from app.repositories.role_repository import RoleRepository
from app.repositories.user_repository import UserRepository
from app.schemas.auth import (
    ChangePasswordRequest,
    TokenResponse,
    UserLogin,
    UserProfileUpdate,
    UserRegister,
    UserResponse,
)
from app.services.base import BaseService

logger = logging.getLogger(__name__)


class AuthService(BaseService):
    """Service xử lý nghiệp vụ xác thực tài khoản và phân quyền."""

    def __init__(self) -> None:
        self.user_repo = UserRepository()
        self.role_repo = RoleRepository()

    def register(self, db: Session, data: UserRegister) -> UserResponse:
        """Đăng ký tài khoản mới với vai trò mặc định là 'user'."""
        clean_email = data.email.strip().lower()

        # 1. Kiểm tra email đã tồn tại chưa
        if self.user_repo.get_by_email(db, clean_email):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email này đã được sử dụng trong hệ thống",
            )

        # 2. Lấy role mặc định 'user'
        user_role = self.role_repo.get_by_name(db, "user")
        if not user_role:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Chưa cấu hình vai trò mặc định 'user'",
            )

        # 3. Băm mật khẩu và tạo bản ghi
        hashed_password = get_password_hash(data.password)
        new_user = User(
            email=clean_email,
            full_name=data.full_name,
            password_hash=hashed_password,
            role_id=user_role.id,
            is_active=True,
        )

        self.user_repo.create(db, new_user)
        self.commit_or_rollback(db, conflict_detail="Email này đã được sử dụng trong hệ thống")
        db.refresh(new_user)
        return UserResponse.from_orm_model(new_user)

    def login(self, db: Session, data: UserLogin) -> TokenResponse:
        """Xác thực đăng nhập và trả về JWT Access Token."""
        clean_email = data.email.strip().lower()
        user = self.user_repo.get_by_email(db, clean_email)

        if not user or not verify_password(data.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email hoặc mật khẩu không chính xác",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Tài khoản của bạn đã bị khóa hoặc vô hiệu hóa",
            )

        role_name = user.role.name if user.role else "user"
        access_token = create_access_token(
            data={"sub": str(user.id), "email": user.email, "role": role_name}
        )

        return TokenResponse(access_token=access_token, token_type="bearer")

    def logout(self, token: str, redis_client: Any) -> dict[str, str]:
        """Thu hồi access token hiện tại bằng cách thêm mã định danh jti vào blacklist Redis."""
        try:
            payload = decode_access_token(token)
            jti = payload.get("jti")
            exp = payload.get("exp")
            if jti and exp:
                now = datetime.now(timezone.utc).timestamp()
                remaining_ttl = int(exp - now)
                # Chỉ đưa vào blacklist nếu token chưa hết hạn tự nhiên
                if remaining_ttl > 0:
                    redis_client.set(f"blacklist:{jti}", "revoked", ex=remaining_ttl)
                    logger.info("Đã đưa token jti=%s vào blacklist (ttl=%d giây)", jti, remaining_ttl)
        except Exception as exc:
            logger.warning("Lỗi thu hồi token khi đăng xuất: %s", exc)

        return {"message": "Đăng xuất thành công"}

    def get_me(self, current_user: User) -> UserResponse:
        """Trả về thông tin chi tiết của người dùng hiện tại."""
        return UserResponse.from_orm_model(current_user)

    def update_profile(
        self, db: Session, user: User, data: UserProfileUpdate
    ) -> UserResponse:
        """Cập nhật thông tin họ và tên cá nhân."""
        user.full_name = data.full_name.strip()
        self.commit_or_rollback(db, conflict_detail="Could not update profile")
        db.refresh(user)
        return UserResponse.from_orm_model(user)

    def change_password(
        self, db: Session, user: User, data: ChangePasswordRequest
    ) -> dict[str, str]:
        """Đổi mật khẩu người dùng sau khi xác thực mật khẩu cũ."""
        if not verify_password(data.old_password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Mật khẩu hiện tại không chính xác",
            )

        user.password_hash = get_password_hash(data.new_password)
        self.commit_or_rollback(db, conflict_detail="Could not change password")
        return {"message": "Đổi mật khẩu thành công"}
