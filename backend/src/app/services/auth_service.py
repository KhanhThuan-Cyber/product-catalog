import logging
from datetime import datetime, timezone
from typing import Any
from fastapi import HTTPException, status
from redis.exceptions import WatchError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core import redis as redis_module
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_access_token,
    decode_refresh_token,
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

    def login(
        self,
        db: Session,
        data: UserLogin,
        redis_client: Any = None,
    ) -> TokenResponse:
        """Xác thực đăng nhập và phát hành cặp Access Token + Refresh Token."""
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

        # 1. Tạo access token
        role_name = user.role.name if user.role else "user"
        access_token = create_access_token(
            data={"sub": str(user.id), "email": user.email, "role": role_name}
        )

        # 2. Tạo refresh token và lưu vào Redis
        refresh_token, jti = create_refresh_token(user.id)
        client = redis_client or redis_module.redis_client
        ttl_seconds = settings.REFRESH_TOKEN_EXPIRE_DAYS * 86400
        try:
            client.set(f"refresh:{user.id}:{jti}", "active", ex=ttl_seconds)
            logger.info("Đã phát hành refresh token cho user_id=%s, jti=%s", user.id, jti)
        except Exception as exc:
            logger.warning("Lỗi lưu refresh token vào Redis: %s", exc)

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
        )

    def refresh_token(
        self,
        db: Session,
        old_refresh_token: str,
        redis_client: Any = None,
    ) -> TokenResponse:
        """Thực hiện refresh token rotation với cơ chế kiểm tra tái sử dụng nguyên tử (WATCH/MULTI/EXEC)."""
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token không hợp lệ hoặc đã hết hạn",
            headers={"WWW-Authenticate": "Bearer"},
        )

        try:
            payload = decode_refresh_token(old_refresh_token)
            user_id_str = payload.get("sub")
            old_jti = payload.get("jti")
            if not user_id_str or not old_jti:
                raise credentials_exception
            user_id = int(user_id_str)
        except Exception:
            raise credentials_exception

        # Xác thực user trong cơ sở dữ liệu
        user = self.user_repo.get_by_id(db, user_id)
        if not user or not user.is_active:
            raise credentials_exception

        client = redis_client or redis_module.redis_client

        # Chuẩn bị cặp token mới
        role_name = user.role.name if user.role else "user"
        new_access_token = create_access_token(
            data={"sub": str(user.id), "email": user.email, "role": role_name}
        )
        new_refresh_token, new_jti = create_refresh_token(user.id)
        ttl_seconds = settings.REFRESH_TOKEN_EXPIRE_DAYS * 86400

        old_key = f"refresh:{user.id}:{old_jti}"
        new_key = f"refresh:{user.id}:{new_jti}"

        # Thực thi kiểm tra và rotate nguyên tử qua Redis transaction (WATCH / MULTI / EXEC)
        rotate_success = False
        try:
            with client.pipeline(transaction=True) as pipe:
                pipe.watch(old_key)
                if pipe.exists(old_key):
                    pipe.multi()
                    pipe.delete(old_key)
                    pipe.set(new_key, "active", ex=ttl_seconds)
                    pipe.execute()
                    rotate_success = True
                else:
                    pipe.unwatch()
                    rotate_success = False
        except WatchError:
            # Race condition: bị xoay vòng đồng thời bởi request khác
            rotate_success = False
        except Exception as exc:
            logger.warning("Lỗi transaction khi rotate refresh token: %s", exc)
            rotate_success = False

        if not rotate_success:
            # Phát hiện Token Reuse! Key cũ không tồn tại (đã bị dùng trước đó hoặc bị tấn công)
            # Thu hồi toàn bộ session của user để ngăn chặn kẻ tấn công
            self.revoke_all_sessions(user.id, client)
            logger.warning("CẢNH BÁO BẢO MẬT: Phát hiện tái sử dụng refresh token user_id=%s, jti=%s", user.id, old_jti)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Phát hiện hành vi tái sử dụng Refresh Token bất thường. Tất cả các phiên đăng nhập đã bị thu hồi vì lý do an toàn.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        logger.info("Rotate refresh token thành công cho user_id=%s", user.id)
        return TokenResponse(
            access_token=new_access_token,
            refresh_token=new_refresh_token,
            token_type="bearer",
        )

    def revoke_all_sessions(self, user_id: int, redis_client: Any = None) -> int:
        """Thu hồi toàn bộ phiên đăng nhập của người dùng qua SCAN + Pipeline DEL."""
        client = redis_client or redis_module.redis_client
        prefix = f"refresh:{user_id}:"
        revoked_count = 0
        try:
            keys: list[str] = []
            for key in client.scan_iter(match=f"{prefix}*", count=100):
                keys.append(key)

            if keys:
                with client.pipeline(transaction=False) as pipe:
                    for key in keys:
                        pipe.delete(key)
                    pipe.execute()
                revoked_count = len(keys)
            logger.info("Đã thu hồi %d refresh token của user_id=%s", revoked_count, user_id)
        except Exception as exc:
            logger.warning("Lỗi thu hồi toàn bộ session user_id=%s: %s", user_id, exc)

        return revoked_count

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
