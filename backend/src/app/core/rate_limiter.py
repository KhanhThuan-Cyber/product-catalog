"""Module giới hạn tần suất yêu cầu (Rate Limiting) theo thuật toán Fixed Window.

- Sử dụng Redis INCR + EXPIRE đảm bảo hiệu năng cao và độ trễ thấp.
- Hỗ trợ rate limit theo IP (xử lý proxy qua header X-Forwarded-For) và theo Email.
- Cơ chế Fail-Open: Nếu Redis sập hoặc gặp sự cố, hệ thống tự động cho qua (không chặn)
  để ưu tiên tính sẵn sàng cho người dùng hợp pháp.
"""

from __future__ import annotations

import logging
from typing import Any
from fastapi import Depends, HTTPException, Request, status

from app.core.config import settings
from app.core.redis import get_redis
from app.schemas.auth import UserLogin, UserRegister

logger = logging.getLogger(__name__)


def get_client_ip(request: Request) -> str:
    """Trích xuất địa chỉ IP thực tế của client, hỗ trợ trường hợp đứng sau Reverse Proxy / LB."""
    forwarded_for = request.headers.get("x-forwarded-for")
    if forwarded_for:
        # Lấy IP đầu tiên trong danh sách client gửi lên proxy
        client_ip = forwarded_for.split(",")[0].strip()
        if client_ip:
            return client_ip

    if request.client and request.client.host:
        return request.client.host

    return "127.0.0.1"


def check_rate_limit(
    redis_client: Any,
    key: str,
    max_requests: int,
    window_seconds: int,
) -> None:
    """Kiểm tra và tăng số lượng request trong cửa sổ thời gian cố định (Fixed Window).
    
    Raises:
        HTTPException(429): Khi số request vượt quá ngưỡng quy định.
    """
    try:
        current = redis_client.incr(key)
        if current == 1:
            # Request đầu tiên trong window -> thiết lập TTL
            redis_client.expire(key, window_seconds)

        if current > max_requests:
            ttl = redis_client.ttl(key)
            retry_after = ttl if ttl > 0 else window_seconds
            logger.warning("Rate limit vượt ngưỡng cho key '%s' (%d/%d)", key, current, max_requests)
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Quá nhiều yêu cầu. Vui lòng thử lại sau {retry_after} giây.",
                headers={"Retry-After": str(retry_after)},
            )
    except HTTPException:
        raise
    except Exception as exc:
        # Fail-Open: Cho phép request đi tiếp nếu Redis có sự cố
        logger.warning("Lỗi Redis trong quá trình rate limit key '%s': %s (Fail-Open)", key, exc)
        return


def rate_limit_login(
    request: Request,
    data: UserLogin,
    redis: Any = Depends(get_redis),
) -> None:
    """Dependency giới hạn tần suất đăng nhập (theo cả IP và Email)."""
    ip = get_client_ip(request)
    email = data.email.strip().lower()

    # 1. Giới hạn theo IP
    ip_key = f"ratelimit:login:ip:{ip}"
    check_rate_limit(
        redis_client=redis,
        key=ip_key,
        max_requests=settings.RATE_LIMIT_LOGIN_MAX,
        window_seconds=settings.RATE_LIMIT_LOGIN_WINDOW,
    )

    # 2. Giới hạn theo Email (ngăn chặn tấn công brute-force từ nhiều IP phân tán)
    email_key = f"ratelimit:login:email:{email}"
    check_rate_limit(
        redis_client=redis,
        key=email_key,
        max_requests=settings.RATE_LIMIT_LOGIN_MAX,
        window_seconds=settings.RATE_LIMIT_LOGIN_WINDOW,
    )


def rate_limit_register(
    request: Request,
    data: UserRegister,
    redis: Any = Depends(get_redis),
) -> None:
    """Dependency giới hạn tần suất đăng ký tài khoản mới theo IP và Email."""
    ip = get_client_ip(request)
    email = data.email.strip().lower()

    # Giới hạn theo IP
    ip_key = f"ratelimit:register:ip:{ip}"
    check_rate_limit(
        redis_client=redis,
        key=ip_key,
        max_requests=settings.RATE_LIMIT_REGISTER_MAX,
        window_seconds=settings.RATE_LIMIT_REGISTER_WINDOW,
    )

    # Giới hạn theo Email
    email_key = f"ratelimit:register:email:{email}"
    check_rate_limit(
        redis_client=redis,
        key=email_key,
        max_requests=settings.RATE_LIMIT_REGISTER_MAX,
        window_seconds=settings.RATE_LIMIT_REGISTER_WINDOW,
    )
