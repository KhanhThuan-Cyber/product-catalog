"""Seed dữ liệu mẫu: danh mục và sản phẩm.

Hàm ``seed_products`` idempotent — chạy lại nhiều lần chỉ tạo phần thiếu,
không trùng lặp. Được gọi khi khởi động app (xem ``app.main``) và khi
chạy script ``seed.py`` thủ công.
"""
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.category import Category
from app.models.product import Product

# Số lượng sản phẩm muốn tạo
TOTAL_PRODUCTS = 120

# Danh mục mẫu
CATEGORY_NAMES = [
    "Điện thoại",
    "Laptop",
    "Phụ kiện",
    "Thiết bị mạng",
    "Thiết bị văn phòng",
]

# Tên sản phẩm mẫu
PRODUCT_NAMES = [
    "Điện thoại thông minh",
    "Laptop văn phòng",
    "Tai nghe Bluetooth",
    "Bàn phím cơ",
    "Chuột không dây",
    "Màn hình máy tính",
    "Ổ cứng SSD",
    "RAM máy tính",
    "Router Wi-Fi",
    "Webcam Full HD",
    "Loa Bluetooth",
    "Cáp sạc USB-C",
    "Sạc nhanh",
    "USB lưu trữ",
    "Máy in laser",
    "Bàn di chuột",
    "Giá đỡ laptop",
    "Microphone USB",
    "Hub USB",
    "Ổ cắm điện thông minh",
]


def seed_products(db: Session) -> None:
    """Tạo danh mục và sản phẩm mẫu nếu chưa tồn tại (idempotent)."""
    # 1. Tạo danh mục nếu chưa tồn tại
    categories = db.scalars(select(Category)).all()

    existing_names = {category.name.lower() for category in categories}

    for name in CATEGORY_NAMES:
        if name.lower() not in existing_names:
            db.add(Category(name=name))

    db.flush()

    # Đọc lại danh mục để lấy ID
    categories = db.scalars(select(Category).order_by(Category.id)).all()

    if not categories:
        raise RuntimeError("Không có danh mục để tạo sản phẩm.")

    # 2. Lấy tên sản phẩm hiện có để tránh tạo trùng
    existing_product_names = set(db.scalars(select(Product.name)).all())

    created = 0
    skipped = 0

    # 3. Sinh sản phẩm
    for i in range(1, TOTAL_PRODUCTS + 1):
        base_name = PRODUCT_NAMES[(i - 1) % len(PRODUCT_NAMES)]
        name = f"{base_name} Model {i:03d}"

        # Nếu tên đã tồn tại thì bỏ qua (idempotent)
        if name in existing_product_names:
            skipped += 1
            continue

        # Giá từ 100.000 đến 20.000.000
        price = Decimal(100_000 + (i * 137_000) % 19_900_000)

        # Luân phiên các danh mục
        category = categories[(i - 1) % len(categories)]

        product = Product(
            name=name,
            description=(
                f"{name}. Sản phẩm dữ liệu mẫu "
                f"dùng để kiểm thử API, mã SEED-{i:04d}."
            ),
            price=price,
            stock=(i * 7) % 201,
            category_id=category.id,
        )

        db.add(product)
        existing_product_names.add(name)
        created += 1

    db.commit()

    print("=" * 45)
    print("SEED PRODUCTS COMPLETED")
    print(f"Created : {created}")
    print(f"Skipped : {skipped}")
    print(f"Target  : {TOTAL_PRODUCTS}")
    print("=" * 45)
