import os
import sys
from pathlib import Path
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool
from alembic import context
from dotenv import load_dotenv

# Load biến môi trường từ .env
load_dotenv(Path(__file__).resolve().parents[1] / ".env")

# Thêm thư mục src vào sys.path để import app modules
SRC_DIR = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(SRC_DIR))

# Import Base và tất cả models để autogenerate hoạt động
from app.models.base import Base
from app.models.category import Category
from app.models.product import Product
from app.models.role import Role
from app.models.user import User

# Alembic Config object
config = context.config

# Ghi đè sqlalchemy.url bằng giá trị từ .env
config.set_main_option("sqlalchemy.url", os.environ["DATABASE_URL"])

# Cấu hình logging từ alembic.ini
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Chạy migration ở chế độ offline (không cần kết nối DB thực)."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Chạy migration ở chế độ online (kết nối DB thực)."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
