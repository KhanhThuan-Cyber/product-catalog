from typing import Any
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db, oauth2_scheme
from app.core.rate_limiter import rate_limit_login, rate_limit_register
from app.core.redis import get_redis
from app.models.user import User
from app.schemas.auth import (
    ChangePasswordRequest,
    RefreshTokenRequest,
    TokenResponse,
    UserLogin,
    UserProfileUpdate,
    UserRegister,
    UserResponse,
)
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])
auth_service = AuthService()


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Đăng ký tài khoản người dùng mới",
    dependencies=[Depends(rate_limit_register)],
)
def register(
    data: UserRegister,
    db: Session = Depends(get_db),
):
    """Đăng ký tài khoản mới trong hệ thống.
    
    - Mặc định được gán vai trò: `user`.
    - Mật khẩu được băm an toàn bằng BCrypt trước khi lưu.
    - Được bảo vệ bởi Fixed-Window Rate Limiter.
    """
    return auth_service.register(db, data)


@router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Đăng nhập tài khoản và nhận Access Token",
    dependencies=[Depends(rate_limit_login)],
)
def login(
    data: UserLogin,
    db: Session = Depends(get_db),
    redis: Any = Depends(get_redis),
):
    """Xác thực thông tin tài khoản bằng Email và Mật khẩu.
    
    - Trả về JWT Access Token và Refresh Token nếu thông tin chính xác.
    - Token được sử dụng cho header `Authorization: Bearer <token>`.
    - Được bảo vệ bởi Fixed-Window Rate Limiter theo cả IP và Email.
    """
    return auth_service.login(db, data, redis_client=redis)


@router.post(
    "/refresh",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Cấp mới Access Token bằng Refresh Token (Token Rotation)",
)
def refresh(
    data: RefreshTokenRequest,
    db: Session = Depends(get_db),
    redis: Any = Depends(get_redis),
):
    """Thực hiện xoay vòng Refresh Token. Nếu phát hiện token đã được dùng,
    toàn bộ phiên làm việc của tài khoản sẽ bị thu hồi ngay lập tức.
    """
    return auth_service.refresh_token(db, data.refresh_token, redis_client=redis)


@router.post(
    "/revoke-all",
    status_code=status.HTTP_200_OK,
    summary="Thu hồi toàn bộ phiên đăng nhập của tài khoản",
)
def revoke_all(
    current_user: User = Depends(get_current_user),
    redis: Any = Depends(get_redis),
):
    """Đăng xuất khỏi tất cả các thiết bị bằng cách xóa toàn bộ Refresh Token của user."""
    count = auth_service.revoke_all_sessions(current_user.id, redis_client=redis)
    return {"message": f"Đã thu hồi thành công {count} phiên đăng nhập"}


@router.post(
    "/logout",
    status_code=status.HTTP_200_OK,
    summary="Đăng xuất và thu hồi Access Token hiện tại",
)
def logout(
    token: str = Depends(oauth2_scheme),
    current_user: User = Depends(get_current_user),
    redis: Any = Depends(get_redis),
):
    """Đăng xuất tài khoản bằng cách đưa access token hiện tại vào blacklist Redis."""
    return auth_service.logout(token, redis)


@router.get(
    "/me",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Lấy thông tin tài khoản đang đăng nhập",
)
def get_me(
    current_user: User = Depends(get_current_user),
):
    """Truy xuất thông tin hồ sơ của người dùng hiện tại dựa trên Bearer token."""
    return auth_service.get_me(current_user)


@router.patch(
    "/me",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Cập nhật thông tin họ và tên cá nhân",
)
def update_profile(
    data: UserProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Người dùng tự cập nhật họ tên của mình."""
    return auth_service.update_profile(db, current_user, data)


@router.post(
    "/change-password",
    status_code=status.HTTP_200_OK,
    summary="Đổi mật khẩu tài khoản cá nhân",
)
def change_password(
    data: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Người dùng tự đổi mật khẩu sau khi xác minh mật khẩu cũ."""
    return auth_service.change_password(db, current_user, data)
