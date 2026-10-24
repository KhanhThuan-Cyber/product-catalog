import sys
from pathlib import Path

# Đảm bảo thư mục src nằm trong sys.path khi chạy script độc lập
sys.path.insert(0, str(Path(__file__).parent / "src"))

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import engine
from app.models.base import Base
from app.models.category import Category
from app.models.product import Product


def seed_categories(db: Session) -> None:
    categories = [
        {"name": "Laptop", "description": "Máy tính xách tay"},
        {"name": "Smartphone", "description": "Điện thoại thông minh"},
        {"name": "Accessories", "description": "Phụ kiện máy tính và điện thoại"},
        {"name": "Monitor", "description": "Màn hình máy tính"},
        {"name": "Networking", "description": "Thiết bị mạng"},
    ]

    for item in categories:
        existing = db.scalar(select(Category).where(Category.name == item["name"]))
        if existing is None:
            db.add(Category(**item))


def main() -> None:
    Base.metadata.create_all(bind=engine)

    with Session(engine) as db:
        try:
            seed_categories(db)
            db.commit()
            print("Seed dữ liệu thành công!")
        except Exception:
            db.rollback()
            raise


if __name__ == "__main__":
    main()
