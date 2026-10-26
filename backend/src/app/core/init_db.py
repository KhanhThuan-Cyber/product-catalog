import logging
from sqlalchemy import inspect, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session

from app.core.security import get_password_hash
from app.models.base import Base
from app.models.role import Role
from app.models.user import User

logger = logging.getLogger(__name__)

DEFAULT_ROLES = [
    {"name": "admin", "description": "Quản trị viên toàn quyền hệ thống"},
    {"name": "user", "description": "Người dùng thông thường"},
]

DEFAULT_ADMIN_EMAIL = "admin@system.local"
DEFAULT_ADMIN_PASSWORD = "Admin@123456"


def auto_upgrade_schema(engine: Engine) -> None:
    """Tự động kiểm tra và nâng cấp Schema nếu bảng cũ đã tồn tại trong DB."""
    inspector = inspect(engine)
    existing_tables = inspector.get_table_names()

    # 1. Nếu bảng users đã tồn tại từ trước, kiểm tra và nâng cấp cột password_hash lên VARCHAR(255)
    if "users" in existing_tables:
        columns = {col["name"]: col for col in inspector.get_columns("users")}
        pwd_col = columns.get("password_hash")

        if pwd_col and hasattr(pwd_col["type"], "length") and (pwd_col["type"].length or 0) < 255:
            logger.info("--> Phát hiện cột password_hash cũ (< 255), đang tự động nâng cấp...")
            dialect_name = engine.dialect.name
            try:
                with engine.begin() as conn:
                    if dialect_name == "postgresql":
                        conn.execute(text("ALTER TABLE users ALTER COLUMN password_hash TYPE VARCHAR(255);"))
                        conn.execute(text("ALTER TABLE users ALTER COLUMN password_hash SET NOT NULL;"))
                    logger.info("✓ Nâng cấp cột password_hash lên VARCHAR(255) thành công.")
            except Exception as e:
                logger.warning(f"Không thể tự động ALTER TABLE users: {e}")

    # 2. Tạo tất cả các bảng chưa tồn tại
    Base.metadata.create_all(bind=engine)


def init_default_roles(db: Session) -> None:
    """Đảm bảo các role mặc định (admin, user) luôn tồn tại trong DB."""
    for role_info in DEFAULT_ROLES:
        role = db.query(Role).filter(Role.name == role_info["name"]).first()
        if not role:
            logger.info(f"--> Khởi tạo vai trò mặc định: '{role_info['name']}'...")
            new_role = Role(
                name=role_info["name"],
                description=role_info["description"],
            )
            db.add(new_role)
    db.commit()


def init_super_admin(db: Session) -> None:
    """Tự động tạo tài khoản Super Admin ban đầu nếu hệ thống chưa có Admin."""
    admin_role = db.query(Role).filter(Role.name == "admin").first()
    if not admin_role:
        return

    admin_user = (
        db.query(User)
        .filter((User.role_id == admin_role.id) | (User.email == DEFAULT_ADMIN_EMAIL))
        .first()
    )

    if not admin_user:
        logger.info(f"--> Khởi tạo tài khoản Super Admin mặc định: {DEFAULT_ADMIN_EMAIL}...")
        super_admin = User(
            email=DEFAULT_ADMIN_EMAIL,
            full_name="System Administrator",
            password_hash=get_password_hash(DEFAULT_ADMIN_PASSWORD),
            role_id=admin_role.id,
            is_active=True,
        )
        db.add(super_admin)
        db.commit()
        logger.info(f"✓ Tạo Super Admin thành công (Mật khẩu: {DEFAULT_ADMIN_PASSWORD}).")


def init_database(engine: Engine, session_factory) -> None:
    """Quy trình toàn diện tự động chạy khi khởi động server:
    
    1. Tự động kiểm tra và nâng cấp schema nếu bảng cũ tồn tại.
    2. Tự động tạo các bảng mới chưa có.
    3. Tự động seed roles 'admin' & 'user' nếu chưa có.
    4. Tự động tạo tài khoản super admin nếu chưa có.
    """
    # Bước 1 & 2: Schema Migration & Creation
    auto_upgrade_schema(engine)

    # Bước 3 & 4: Data Bootstrapping
    db = session_factory()
    try:
        init_default_roles(db)
        init_super_admin(db)
    finally:
        db.close()
