from typing import Any
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db, oauth2_scheme
from app.core.redis import get_redis
from app.models.user import User
from app.schemas.auth import (
    ChangePasswordRequest,
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
)
def register(
    data: UserRegister,
    db: Session = Depends(get_db),
):
    """Đăng ký tài khoản mới trong hệ thống.
    
    - Mặc định được gán vai trò: `user`.
    - Mật khẩu được băm an toàn bằng BCrypt trước khi lưu.
    """
    return auth_service.register(db, data)


@router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Đăng nhập tài khoản và nhận Access Token",
)
def login(
    data: UserLogin,
    db: Session = Depends(get_db),
):
    """Xác thực thông tin tài khoản bằng Email và Mật khẩu.
    
    - Trả về JWT Access Token nếu thông tin chính xác.
    - Token được sử dụng cho header `Authorization: Bearer <token>`.
    """
    return auth_service.login(db, data)


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
