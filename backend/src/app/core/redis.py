"""Quản lý kết nối Redis và fallback an toàn khi Redis không khả dụng.

Client được khởi tạo ở mức module (singleton), khớp với pattern hiện tại
của ``engine`` / ``SessionLocal`` / ``settings``. Khi Redis sập, một
``NoOpRedisClient`` được dùng thay thế để ứng dụng vẫn chạy bình thường
(cache miss, rate-limit fail-open, không crash).

Lưu ý cho tầng Service: nên resolve client qua ``app.core.redis.redis_client``
(mỗi lời gọi đọc giá trị mới nhất) thay vì import trực tiếp giá trị tại thời
điểm import, để test có thể thay thế singleton bằng fakeredis.
"""

from __future__ import annotations

import logging
from typing import Any, Iterator

import redis
from redis.exceptions import RedisError

from app.core.config import settings

logger = logging.getLogger(__name__)


class NoOpRedisClient:
    """Client thay thế khi Redis không khả dụng. Mọi thao tác là no-op, không raise.

    - Cache layer: coi no-op như cache miss (``get`` trả ``None``).
    - Rate limiter: fail-open (``incr`` trả 0 => không bao giờ chặn request).
    - ``scan_iter`` trả iterator rỗng để ``delete_by_prefix`` an toàn.
    """

    # --- Lệnh cơ bản ---
    def get(self, name: str | bytes) -> None:
        return None

    def set(
        self,
        name: str | bytes,
        value: Any,
        ex: int | None = None,
        **kwargs: Any,
    ) -> bool:
        return False

    def setex(self, name: str | bytes, time: int, value: Any) -> bool:
        return False

    def delete(self, *names: str | bytes) -> int:
        return 0

    def exists(self, *names: str | bytes) -> int:
        return 0

    def incr(self, name: str | bytes, amount: int = 1) -> int:
        return 0

    def expire(self, name: str | bytes, time: int) -> bool:
        return False

    def ttl(self, name: str | bytes) -> int:
        return -2  # -2 = key không tồn tại (theo semantics Redis)

    def ping(self) -> bool:
        return False

    def close(self) -> None:
        pass

    # --- SCAN: trả iterator rỗng ---
    def scan_iter(
        self,
        match: str | None = None,
        count: int | None = None,
    ) -> Iterator[str]:
        return iter(())

    # --- Pipeline no-op cho delete_by_prefix ---
    def pipeline(
        self,
        transaction: bool = True,
        shard_hint: str | None = None,
    ) -> "_NoOpPipeline":
        return _NoOpPipeline()


class _NoOpPipeline:
    """Pipeline no-op dùng khi Redis sập (cho ``delete_by_prefix``)."""

    def delete(self, *names: str | bytes) -> "_NoOpPipeline":
        return self

    def execute(self) -> list[Any]:
        return []

    def __enter__(self) -> "_NoOpPipeline":
        return self

    def __exit__(self, *exc: Any) -> bool:
        return False


def _create_redis_client() -> "redis.Redis | NoOpRedisClient":
    """Tạo Redis client; fallback NoOp nếu kết nối thất bại.

    Timeout ngắn để không làm chậm startup quá lâu khi Redis không khả dụng.
    """
    try:
        client = redis.Redis.from_url(
            settings.REDIS_URL,
            decode_responses=True,
            socket_connect_timeout=2,
            socket_timeout=2,
        )
        client.ping()
        logger.info("--> Kết nối Redis thành công: %s", settings.REDIS_URL)
        return client
    except RedisError as exc:
        logger.warning(
            "Không kết nối được Redis (%s). "
            "Cache/rate-limit sẽ chạy ở chế độ fallback (no-op).",
            exc,
        )
        return NoOpRedisClient()


# Singleton mức module (giống engine / SessionLocal / settings)
redis_client: "redis.Redis | NoOpRedisClient" = _create_redis_client()


def get_redis() -> "redis.Redis | NoOpRedisClient":
    """FastAPI dependency trả về Redis client hiện tại.

    Dùng cho các endpoint cần truy cập trực tiếp Redis (vd: logout / revoke token).
    Tầng Service nên resolve client qua ``app.core.redis.redis_client`` (lazy)
    để test có thể thay thế bằng fakeredis.
    """
    return redis_client
