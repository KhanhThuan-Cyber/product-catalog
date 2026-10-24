from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.api.deps import get_db
from app.core.init_db import init_default_roles, init_super_admin
from app.main import app
from app.models.base import Base

# Thiết lập database SQLite in-memory độc lập cho bài test
test_engine = create_engine("sqlite:///:memory:")
Base.metadata.create_all(bind=test_engine)
TestingSessionLocal = sessionmaker(bind=test_engine)

# Khởi tạo sẵn roles và super admin
with TestingSessionLocal() as setup_db:
    init_default_roles(setup_db)
    init_super_admin(setup_db)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


def test_register_user_success():
    payload = {
        "email": "testuser@example.com",
        "password": "Password@123",
        "full_name": "Test User",
    }
    response = client.post("/Thuancyber/auth/register", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "testuser@example.com"
    assert data["full_name"] == "Test User"
    assert data["role_name"] == "user"
    assert data["is_active"] is True
    assert "id" in data


def test_register_duplicate_email_conflict():
    payload = {
        "email": "testuser@example.com",  # Email đã đăng ký ở test trên
        "password": "AnotherPassword123",
        "full_name": "Duplicate User",
    }
    response = client.post("/Thuancyber/auth/register", json=payload)
    assert response.status_code == 409
    assert "đã được sử dụng" in response.json()["detail"]


def test_login_success_and_failure():
    # 1. Đăng nhập đúng
    login_payload = {
        "email": "testuser@example.com",
        "password": "Password@123",
    }
    response = client.post("/Thuancyber/auth/login", json=login_payload)
    assert response.status_code == 200
    token_data = response.json()
    assert "access_token" in token_data
    assert token_data["token_type"] == "bearer"

    # 2. Đăng nhập sai mật khẩu
    wrong_payload = {
        "email": "testuser@example.com",
        "password": "WrongPassword999",
    }
    wrong_res = client.post("/Thuancyber/auth/login", json=wrong_payload)
    assert wrong_res.status_code == 401

    # 3. Đăng nhập tài khoản không tồn tại
    non_exist_res = client.post(
        "/Thuancyber/auth/login",
        json={"email": "nobody@example.com", "password": "password"},
    )
    assert non_exist_res.status_code == 401


def test_get_me_endpoint():
    # Đăng nhập lấy token
    login_res = client.post(
        "/Thuancyber/auth/login",
        json={"email": "testuser@example.com", "password": "Password@123"},
    )
    token = login_res.json()["access_token"]

    # 1. Gọi /auth/me với token hợp lệ
    headers = {"Authorization": f"Bearer {token}"}
    me_res = client.get("/Thuancyber/auth/me", headers=headers)
    assert me_res.status_code == 200
    me_data = me_res.json()
    assert me_data["email"] == "testuser@example.com"
    assert me_data["role_name"] == "user"

    # 2. Gọi /auth/me không có token
    no_token_res = client.get("/Thuancyber/auth/me")
    assert no_token_res.status_code == 401

    # 3. Gọi /auth/me với token giả mạo
    fake_token_res = client.get(
        "/Thuancyber/auth/me",
        headers={"Authorization": "Bearer fake.token.here"},
    )
    assert fake_token_res.status_code == 401


def test_profile_update_and_change_password():
    # Đăng nhập lấy token
    login_res = client.post(
        "/Thuancyber/auth/login",
        json={"email": "testuser@example.com", "password": "Password@123"},
    )
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Cập nhật họ tên (PATCH /auth/me)
    patch_res = client.patch(
        "/Thuancyber/auth/me",
        headers=headers,
        json={"full_name": "Nguyễn Văn Đã Đổi Tên"},
    )
    assert patch_res.status_code == 200
    assert patch_res.json()["full_name"] == "Nguyễn Văn Đã Đổi Tên"

    # 2. Đổi mật khẩu với mật khẩu cũ sai
    bad_pwd_res = client.post(
        "/Thuancyber/auth/change-password",
        headers=headers,
        json={"old_password": "WrongOldPassword", "new_password": "NewPassword@456"},
    )
    assert bad_pwd_res.status_code == 400

    # 3. Đổi mật khẩu thành công
    good_pwd_res = client.post(
        "/Thuancyber/auth/change-password",
        headers=headers,
        json={"old_password": "Password@123", "new_password": "NewPassword@456"},
    )
    assert good_pwd_res.status_code == 200
    assert good_pwd_res.json()["message"] == "Đổi mật khẩu thành công"

    # 4. Xác nhận đăng nhập lại bằng mật khẩu mới
    new_login = client.post(
        "/Thuancyber/auth/login",
        json={"email": "testuser@example.com", "password": "NewPassword@456"},
    )
    assert new_login.status_code == 200


def test_admin_create_user_endpoint():
    # 1. Đăng nhập Super Admin
    admin_login = client.post(
        "/Thuancyber/auth/login",
        json={"email": "admin@system.local", "password": "Admin@123456"},
    )
    admin_token = admin_login.json()["access_token"]
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    # 2. Admin tạo user mới với vai trò Admin
    create_res = client.post(
        "/Thuancyber/users",
        headers=admin_headers,
        json={
            "email": "manager@example.com",
            "full_name": "Manager User",
            "password": "Manager@123456",
            "role_id": 1,  # Admin role
        },
    )
    assert create_res.status_code == 201
    created_data = create_res.json()
    assert created_data["email"] == "manager@example.com"
    assert created_data["role_name"] == "admin"

    # 3. User thường cố tạo user -> Bị 403 Forbidden
    user_login = client.post(
        "/Thuancyber/auth/login",
        json={"email": "testuser@example.com", "password": "NewPassword@456"},
    )
    user_token = user_login.json()["access_token"]
    user_headers = {"Authorization": f"Bearer {user_token}"}

    forbidden_res = client.post(
        "/Thuancyber/users",
        headers=user_headers,
        json={
            "email": "hacker@example.com",
            "full_name": "Hacker",
            "password": "Password@123",
            "role_id": 1,
        },
    )
    assert forbidden_res.status_code == 403


def test_admin_create_role_endpoint():
    # 1. Đăng nhập Super Admin
    admin_login = client.post(
        "/Thuancyber/auth/login",
        json={"email": "admin@system.local", "password": "Admin@123456"},
    )
    admin_token = admin_login.json()["access_token"]
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    # 2. Admin tạo vai trò mới (moderator)
    create_role_res = client.post(
        "/Thuancyber/users/roles",
        headers=admin_headers,
        json={
            "name": "moderator",
            "description": "Điều hành viên kiểm duyệt nội dung",
        },
    )
    assert create_role_res.status_code == 201
    role_data = create_role_res.json()
    assert role_data["name"] == "moderator"
    assert role_data["description"] == "Điều hành viên kiểm duyệt nội dung"
    assert "id" in role_data

    # 3. Tạo trùng tên role -> 409 Conflict
    dup_res = client.post(
        "/Thuancyber/users/roles",
        headers=admin_headers,
        json={
            "name": "MODERATOR",  # Kiểm tra chuẩn hóa hoa/thường
            "description": "Trùng tên",
        },
    )
    assert dup_res.status_code == 409
    assert "đã tồn tại" in dup_res.json()["detail"]

    # 4. User thường cố tạo role -> 403 Forbidden
    user_login = client.post(
        "/Thuancyber/auth/login",
        json={"email": "testuser@example.com", "password": "NewPassword@456"},
    )
    user_token = user_login.json()["access_token"]
    user_headers = {"Authorization": f"Bearer {user_token}"}

    forbidden_res = client.post(
        "/Thuancyber/users/roles",
        headers=user_headers,
        json={"name": "hacker_role"},
    )
    assert forbidden_res.status_code == 403

    # 5. Kiểm tra danh sách roles trả về có chứa role vừa tạo
    roles_res = client.get("/Thuancyber/users/roles")
    assert roles_res.status_code == 200
    roles_list = roles_res.json()
    role_names = [r["name"] for r in roles_list]
    assert "moderator" in role_names
    assert "admin" in role_names
    assert "user" in role_names
