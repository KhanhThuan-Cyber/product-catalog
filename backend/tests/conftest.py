"""Pytest fixtures dùng chung cho toàn bộ test suite.

Commit 1: thay Redis client thật bằng ``fakeredis`` (in-memory) để bộ test
chạy độc lập, không cần Redis server. Mỗi test nhận một fake client riêng
(cách ly state) và ghi đè cả ``get_redis`` dependency để các endpoint truy
cập Redis trực tiếp cũng dùng được fake client.
"""

from __future__ import annotations

import pytest
import fakeredis

from app.core import redis as redis_module
from app.core.redis import get_redis
from app.main import app


def _make_fake_redis() -> fakeredis.FakeStrictRedis:
    """Tạo một fakeredis client mới, cách ly hoàn toàn (server riêng)."""
    return fakeredis.FakeStrictRedis(decode_responses=True)


@pytest.fixture(autouse=True)
def _isolated_fake_redis() -> fakeredis.FakeStrictRedis:
    """Cấp fakeredis riêng cho mỗi test, ghi đè singleton + dependency.

    - Thay ``app.core.redis.redis_client`` (singleton) bằng fake →
      các Service resolve client lazy sẽ nhận được fake.
    - Ghi đè ``app.dependency_overrides[get_redis]`` → các endpoint
      dùng ``Depends(get_redis)`` cũng nhận được fake.
    - Khôi phục trạng thái gốc sau khi test kết thúc.
    """
    original = redis_module.redis_client
    fake = _make_fake_redis()
    redis_module.redis_client = fake
    app.dependency_overrides[get_redis] = lambda: fake
    try:
        yield fake
    finally:
        app.dependency_overrides.pop(get_redis, None)
        redis_module.redis_client = original
