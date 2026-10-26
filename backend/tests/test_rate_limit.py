"""Unit tests cho Commit 6 — Rate Limiting (Fixed Window, IP + Email, Fail-Open)."""

from __future__ import annotations

from unittest.mock import MagicMock
import pytest
from fastapi import HTTPException, Request

from app.core import redis as redis_module
from app.core.rate_limiter import (
    check_rate_limit,
    get_client_ip,
    rate_limit_login,
    rate_limit_register,
)
from app.core.redis import NoOpRedisClient
from app.schemas.auth import UserLogin, UserRegister


def make_mock_request(client_host: str = "192.168.1.10", x_forwarded_for: str | None = None) -> Request:
    req = MagicMock(spec=Request)
    req.client.host = client_host
    headers = {}
    if x_forwarded_for:
        headers["x-forwarded-for"] = x_forwarded_for
    req.headers.get.side_effect = lambda k, default=None: headers.get(k.lower(), default)
    return req


def test_get_client_ip_direct_and_forwarded():
    # 1. Trực tiếp từ request.client.host
    direct_req = make_mock_request(client_host="203.0.113.195")
    assert get_client_ip(direct_req) == "203.0.113.195"

    # 2. Qua proxy với X-Forwarded-For
    proxy_req = make_mock_request(
        client_host="10.0.0.1",
        x_forwarded_for="198.51.100.42, 10.0.0.1, 172.16.0.1",
    )
    assert get_client_ip(proxy_req) == "198.51.100.42"


def test_check_rate_limit_fixed_window():
    client = redis_module.redis_client
    key = "test:rl:key"

    # Cấu hình max = 3 requests trong window 60s
    for i in range(1, 4):
        check_rate_limit(client, key, max_requests=3, window_seconds=60)
        assert client.get(key) == str(i)

    # Request thứ 4 vượt ngưỡng -> 429 Too Many Requests
    with pytest.raises(HTTPException) as exc_info:
        check_rate_limit(client, key, max_requests=3, window_seconds=60)

    assert exc_info.value.status_code == 429
    assert "Quá nhiều yêu cầu" in exc_info.value.detail
    assert "Retry-After" in exc_info.value.headers
    assert int(exc_info.value.headers["Retry-After"]) > 0


def test_rate_limit_fail_open_on_redis_error():
    # Khi Redis gặp sự cố, hệ thống tự động cho qua (Fail-Open)
    failing_client = MagicMock()
    failing_client.incr.side_effect = Exception("Redis cluster unavailable")

    # Không raise exception
    check_rate_limit(failing_client, "any:key", max_requests=5, window_seconds=60)


def test_rate_limit_fail_open_with_noop_client():
    # Khi dùng NoOp client (chế độ Redis sập lúc khởi động)
    noop = NoOpRedisClient()
    for _ in range(100):
        check_rate_limit(noop, "any:key", max_requests=5, window_seconds=60)


def test_rate_limit_login_by_ip_and_email():
    client = redis_module.redis_client
    req = make_mock_request(client_host="1.2.3.4")
    login_data = UserLogin(email="target@company.com", password="pwd")

    # Giả lập 10 lần login hợp lệ (ngưỡng max=10)
    for _ in range(10):
        rate_limit_login(req, login_data, redis=client)

    # Lần thứ 11 từ cùng IP/Email -> 429
    with pytest.raises(HTTPException) as exc_info:
        rate_limit_login(req, login_data, redis=client)
    assert exc_info.value.status_code == 429


def test_rate_limit_login_blocks_distributed_attack_on_same_email():
    client = redis_module.redis_client
    login_data = UserLogin(email="victim@company.com", password="pwd")

    # Giả lập tấn công brute-force phân tán từ 10 IP khác nhau vào cùng 1 email
    for ip_suffix in range(1, 11):
        req = make_mock_request(client_host=f"100.64.0.{ip_suffix}")
        rate_limit_login(req, login_data, redis=client)

    # Lần thứ 11 từ IP mới (IP thứ 11) nhưng cùng email nạn nhân -> bị chặn bởi email key!
    new_ip_req = make_mock_request(client_host="100.64.0.11")
    with pytest.raises(HTTPException) as exc_info:
        rate_limit_login(new_ip_req, login_data, redis=client)
    assert exc_info.value.status_code == 429


def test_rate_limit_register():
    client = redis_module.redis_client
    req = make_mock_request(client_host="9.9.9.9")
    reg_data = UserRegister(email="bot@test.com", password="Password@123")

    # Ngưỡng đăng ký: 5 requests
    for _ in range(5):
        rate_limit_register(req, reg_data, redis=client)

    # Lần thứ 6 -> 429
    with pytest.raises(HTTPException) as exc_info:
        rate_limit_register(req, reg_data, redis=client)
    assert exc_info.value.status_code == 429
