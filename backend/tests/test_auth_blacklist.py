"""Unit tests cho Commit 4 — Token Blacklist & Logout."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock

import jwt
import pytest
from fastapi import HTTPException

from app.api.deps import get_current_user
from app.core import redis as redis_module
from app.core.config import settings
from app.core.security import create_access_token, decode_access_token
from app.models.role import Role
from app.models.user import User
from app.routers.auth import logout
from app.services.auth_service import AuthService


@pytest.fixture
def mock_user() -> User:
    role = Role(id=1, name="user")
    user = User(
        id=99,
        email="user@test.com",
        full_name="Test User",
        role_id=1,
        is_active=True,
    )
    user.role = role
    return user


def test_create_access_token_includes_unique_jti():
    token1 = create_access_token({"sub": "1"})
    token2 = create_access_token({"sub": "1"})

    payload1 = decode_access_token(token1)
    payload2 = decode_access_token(token2)

    assert "jti" in payload1
    assert "jti" in payload2
    assert payload1["jti"] != payload2["jti"]


def test_get_current_user_valid_token(mock_user):
    token = create_access_token({"sub": "99"})
    mock_db = MagicMock()

    with pytest.MonkeyPatch.context() as mp:
        mp.setattr("app.api.deps.user_repo.get_by_id", lambda db, uid: mock_user)
        user = get_current_user(token=token, db=mock_db)
        assert user.id == 99


def test_get_current_user_blacklisted_token(mock_user):
    token = create_access_token({"sub": "99"})
    payload = decode_access_token(token)
    jti = payload["jti"]

    # Đưa jti vào blacklist của fake client hiện tại
    redis_module.redis_client.set(f"blacklist:{jti}", "revoked", ex=300)

    mock_db = MagicMock()
    with pytest.MonkeyPatch.context() as mp:
        mp.setattr("app.api.deps.user_repo.get_by_id", lambda db, uid: mock_user)
        with pytest.raises(HTTPException) as exc_info:
            get_current_user(token=token, db=mock_db)
        assert exc_info.value.status_code == 401
        assert "thu hồi" in exc_info.value.detail or "đăng xuất" in exc_info.value.detail


def test_get_current_user_rejects_token_without_jti(mock_user):
    # Giả lập token cũ (không có jti) được phát hành trước khi có blacklist
    expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    legacy_token = jwt.encode(
        {"sub": "99", "exp": expire},
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )

    mock_db = MagicMock()
    with pytest.MonkeyPatch.context() as mp:
        mp.setattr("app.api.deps.user_repo.get_by_id", lambda db, uid: mock_user)
        with pytest.raises(HTTPException) as exc_info:
            get_current_user(token=legacy_token, db=mock_db)
        assert exc_info.value.status_code == 401
        assert "mã định danh" in exc_info.value.detail


def test_logout_service_revokes_token_with_remaining_ttl():
    service = AuthService()
    token = create_access_token({"sub": "99"}, expires_delta=timedelta(minutes=10))
    payload = decode_access_token(token)
    jti = payload["jti"]

    res = service.logout(token, redis_module.redis_client)
    assert res == {"message": "Đăng xuất thành công"}

    # jti phải có trong Redis với TTL dương
    assert redis_module.redis_client.get(f"blacklist:{jti}") == "revoked"
    ttl = redis_module.redis_client.ttl(f"blacklist:{jti}")
    assert ttl > 0 and ttl <= 600


def test_logout_endpoint_handler(mock_user):
    token = create_access_token({"sub": "99"})
    payload = decode_access_token(token)
    jti = payload["jti"]

    res = logout(token=token, current_user=mock_user, redis=redis_module.redis_client)
    assert res == {"message": "Đăng xuất thành công"}

    # Token phải nằm trong blacklist
    assert redis_module.redis_client.get(f"blacklist:{jti}") == "revoked"

    # Sau khi logout, gọi get_current_user với token này phải bị chặn
    mock_db = MagicMock()
    with pytest.MonkeyPatch.context() as mp:
        mp.setattr("app.api.deps.user_repo.get_by_id", lambda db, uid: mock_user)
        with pytest.raises(HTTPException) as exc_info:
            get_current_user(token=token, db=mock_db)
        assert exc_info.value.status_code == 401
