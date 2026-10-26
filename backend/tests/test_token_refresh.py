"""Unit tests cho Commit 5 — Refresh Token Rotation & Atomic Reuse Detection."""

from __future__ import annotations

from unittest.mock import MagicMock
import pytest
from fastapi import HTTPException

from app.core import redis as redis_module
from app.core.security import decode_refresh_token
from app.models.role import Role
from app.models.user import User
from app.routers.auth import auth_service as router_auth_service, refresh, revoke_all
from app.schemas.auth import RefreshTokenRequest, UserLogin
from app.services.auth_service import AuthService


@pytest.fixture
def mock_user() -> User:
    role = Role(id=1, name="user")
    user = User(
        id=77,
        email="refresh_tester@test.com",
        full_name="Refresh Tester",
        password_hash="mock_hash",
        role_id=1,
        is_active=True,
    )
    user.role = role
    return user


def test_login_issues_access_and_refresh_tokens(mock_user):
    service = AuthService()
    service.user_repo = MagicMock()
    service.user_repo.get_by_email.return_value = mock_user

    mock_db = MagicMock()
    with pytest.MonkeyPatch.context() as mp:
        mp.setattr("app.services.auth_service.verify_password", lambda p, h: True)
        resp = service.login(mock_db, UserLogin(email="refresh_tester@test.com", password="pwd"))

    assert resp.access_token is not None
    assert resp.refresh_token is not None

    # Kiểm tra payload refresh token
    payload = decode_refresh_token(resp.refresh_token)
    assert payload["sub"] == "77"
    assert payload["type"] == "refresh"
    assert "jti" in payload

    # Kiểm tra key trong Redis
    jti = payload["jti"]
    assert redis_module.redis_client.get(f"refresh:77:{jti}") == "active"
    assert redis_module.redis_client.ttl(f"refresh:77:{jti}") > 0


def test_refresh_token_rotation_success(mock_user):
    service = AuthService()
    service.user_repo = MagicMock()
    service.user_repo.get_by_email.return_value = mock_user
    service.user_repo.get_by_id.return_value = mock_user

    mock_db = MagicMock()
    with pytest.MonkeyPatch.context() as mp:
        mp.setattr("app.services.auth_service.verify_password", lambda p, h: True)
        login_resp = service.login(mock_db, UserLogin(email="refresh_tester@test.com", password="pwd"))

    old_refresh_token = login_resp.refresh_token
    old_jti = decode_refresh_token(old_refresh_token)["jti"]
    assert redis_module.redis_client.get(f"refresh:77:{old_jti}") == "active"

    # Thực hiện xoay vòng token
    rotated = service.refresh_token(mock_db, old_refresh_token)
    assert rotated.access_token is not None
    assert rotated.refresh_token is not None
    assert rotated.refresh_token != old_refresh_token

    new_jti = decode_refresh_token(rotated.refresh_token)["jti"]
    assert new_jti != old_jti

    # Key cũ phải bị xóa khỏi Redis, key mới được cấp
    assert redis_module.redis_client.get(f"refresh:77:{old_jti}") is None
    assert redis_module.redis_client.get(f"refresh:77:{new_jti}") == "active"


def test_token_reuse_detection_revokes_all_sessions(mock_user):
    service = AuthService()
    service.user_repo = MagicMock()
    service.user_repo.get_by_email.return_value = mock_user
    service.user_repo.get_by_id.return_value = mock_user

    mock_db = MagicMock()
    with pytest.MonkeyPatch.context() as mp:
        mp.setattr("app.services.auth_service.verify_password", lambda p, h: True)
        login_resp = service.login(mock_db, UserLogin(email="refresh_tester@test.com", password="pwd"))

    token_v1 = login_resp.refresh_token

    # Lần 1: Xoay vòng hợp lệ lên token_v2
    rotated_v2 = service.refresh_token(mock_db, token_v1)
    jti_v2 = decode_refresh_token(rotated_v2.refresh_token)["jti"]
    assert redis_module.redis_client.get(f"refresh:77:{jti_v2}") == "active"

    # Lần 2: Giả lập kẻ tấn công dùng lại token_v1 đã bị xoay vòng
    with pytest.raises(HTTPException) as exc_info:
        service.refresh_token(mock_db, token_v1)

    assert exc_info.value.status_code == 401
    assert "tái sử dụng" in exc_info.value.detail

    # Cơ chế reuse detection phải thu hồi TOÀN BỘ các phiên của user 77 (kể cả jti_v2 hợp lệ vừa tạo)
    assert redis_module.redis_client.get(f"refresh:77:{jti_v2}") is None


def test_revoke_all_sessions(mock_user):
    service = AuthService()
    client = redis_module.redis_client

    # Tạo 3 session cho user 77 và 1 session cho user khác
    client.set("refresh:77:jti1", "active", ex=3600)
    client.set("refresh:77:jti2", "active", ex=3600)
    client.set("refresh:77:jti3", "active", ex=3600)
    client.set("refresh:88:other", "active", ex=3600)

    revoked = service.revoke_all_sessions(77, client)
    assert revoked == 3

    # Toàn bộ session của user 77 bị xóa
    assert client.get("refresh:77:jti1") is None
    assert client.get("refresh:77:jti2") is None
    assert client.get("refresh:77:jti3") is None
    # User 88 không bị ảnh hưởng
    assert client.get("refresh:88:other") == "active"


def test_refresh_and_revoke_all_endpoint_handlers(mock_user):
    mock_db = MagicMock()
    with pytest.MonkeyPatch.context() as mp:
        mp.setattr("app.services.auth_service.verify_password", lambda p, h: True)
        mp.setattr(router_auth_service.user_repo, "get_by_email", lambda db, email: mock_user)
        mp.setattr(router_auth_service.user_repo, "get_by_id", lambda db, uid: mock_user)

        login_resp = router_auth_service.login(mock_db, UserLogin(email="refresh_tester@test.com", password="pwd"))

        # Test refresh endpoint handler
        req = RefreshTokenRequest(refresh_token=login_resp.refresh_token)
        refreshed_resp = refresh(data=req, db=mock_db, redis=redis_module.redis_client)
        assert refreshed_resp.access_token is not None
        assert refreshed_resp.refresh_token is not None

        # Test revoke-all endpoint handler
        revoke_resp = revoke_all(current_user=mock_user, redis=redis_module.redis_client)
        assert "thu hồi thành công" in revoke_resp["message"]
