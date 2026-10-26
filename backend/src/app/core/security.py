from datetime import datetime, timedelta, timezone
from typing import Any
import uuid
import jwt
from passlib.context import CryptContext

from app.core.config import settings

# Cấu hình mã hóa mật khẩu sử dụng BCrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    """Tạo chuỗi hash an toàn từ mật khẩu người dùng."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Xác thực mật khẩu người dùng nhập vào so với chuỗi hash trong database."""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict[str, Any], expires_delta: timedelta | None = None) -> str:
    """Tạo JWT access token chứa payload dữ liệu, mã định danh duy nhất (jti) và thời hạn hết hạn."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    if "jti" not in to_encode:
        to_encode["jti"] = str(uuid.uuid4())
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def decode_access_token(token: str) -> dict[str, Any]:
    """Giải mã và xác thực tính hợp lệ của JWT access token."""
    return jwt.decode(
        token,
        settings.JWT_SECRET_KEY,
        algorithms=[settings.JWT_ALGORITHM],
    )


def create_refresh_token(
    user_id: int | str,
    expires_delta: timedelta | None = None,
) -> tuple[str, str]:
    """Tạo JWT refresh token với type='refresh', mã định danh jti và thời hạn hết hạn (mặc định 7 ngày)."""
    jti = str(uuid.uuid4())
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    )
    payload = {
        "sub": str(user_id),
        "jti": jti,
        "type": "refresh",
        "exp": expire,
    }
    token = jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return token, jti


def decode_refresh_token(token: str) -> dict[str, Any]:
    """Giải mã và kiểm tra loại token phải là refresh token."""
    payload = jwt.decode(
        token,
        settings.JWT_SECRET_KEY,
        algorithms=[settings.JWT_ALGORITHM],
    )
    if payload.get("type") != "refresh":
        raise jwt.InvalidTokenError("Token không phải là refresh token hợp lệ")
    return payload
