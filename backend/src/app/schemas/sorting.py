from enum import Enum


class SortOrder(str, Enum):
    asc = "asc"
    desc = "desc"


class ProductSortBy(str, Enum):
    id = "id"
    price = "price"
    created_at = "created_at"
    name = "name"
