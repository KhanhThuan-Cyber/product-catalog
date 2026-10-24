from enum import Enum


class SortOrder(str, Enum):
    """Chiều sắp xếp dữ liệu."""
    asc = "asc"
    desc = "desc"


class ProductSortBy(str, Enum):
    """Whitelist các trường cho phép sắp xếp của Product.
    
    Chống hoàn toàn SQL Injection bằng cách giới hạn chặt chẽ
    các trường được phép truyền vào từ phía Client.
    """
    id = "id"
    price = "price"
    created_at = "created_at"
    name = "name"
