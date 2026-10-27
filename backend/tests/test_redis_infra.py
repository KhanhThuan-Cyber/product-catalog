"""Smoke test cho Commit 1 — kiểm tra hạ tầng Redis + fakeredis.

Không kiểm tra logic cache (sẽ có ở Commit 2+), chỉ xác nhận:
- Settings nạp được các cấu hình Redis mới.
- redis_client singleton được tạo (NoOp khi không có Redis server).
- fakeredis override trong conftest hoạt động: trong test, redis_client
  thực sự là fakeredis, và các lệnh get/set/delete chạy được.
- NoOpRedisClient no-op an toàn.
"""

from __future__ import annotations

import fakeredis

from app.core import redis as redis_module
from app.core.config import settings
from app.core.redis import NoOpRedisClient, get_redis


def test_settings_has_redis_config():
    # Có giá trị mặc định hợp lệ
    assert settings.REDIS_URL.startswith("redis://")
    assert settings.CACHE_TTL_PRODUCT_DETAIL > 0
    assert settings.CACHE_TTL_PRODUCT_LIST > 0
    assert settings.CACHE_TTL_CATEGORY > 0
    assert settings.RATE_LIMIT_LOGIN_MAX > 0
    assert settings.RATE_LIMIT_LOGIN_WINDOW > 0
    assert settings.REFRESH_TOKEN_EXPIRE_DAYS > 0


def test_conftest_overrides_redis_with_fakeredis():
    # Conftest (autouse) đã thay redis_client bằng fakeredis
    client = redis_module.redis_client
    assert isinstance(client, fakeredis.FakeStrictRedis)

    client.set("smoke:key", "hello", ex=60)
    assert client.get("smoke:key") == "hello"
    assert client.delete("smoke:key") == 1
    assert client.get("smoke:key") is None


def test_get_redis_dependency_returns_fakeredis():
    # Dependency path cũng dùng được fake client
    client = get_redis()
    assert isinstance(client, fakeredis.FakeStrictRedis)


def test_noop_client_is_safe_no_op():
    noop = NoOpRedisClient()
    assert noop.get("x") is None           # cache miss
    assert noop.set("x", "y", ex=10) is False
    assert noop.delete("x") == 0
    assert noop.exists("x") == 0
    assert noop.incr("rate:k") == 0          # rate-limit fail-open
    assert list(noop.scan_iter(match="*")) == []
    # pipeline no-op
    with noop.pipeline() as pipe:
        pipe.delete("a", "b")
        assert pipe.execute() == []
