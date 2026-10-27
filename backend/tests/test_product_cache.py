"""Unit tests cho Commit 3 — Product Cache với Composite Key và Invalidation."""

from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
from unittest.mock import MagicMock

import pytest
from sqlalchemy.orm import Session

from app.models.category import Category
from app.models.product import Product
from app.schemas.pagination import PaginatedResponse, PaginationParams
from app.schemas.product import (
    ProductCreate,
    ProductPatch,
    ProductResponse,
    ProductUpdate,
)
from app.schemas.product_filter import ProductFilter
from app.schemas.sorting import ProductSortBy, SortOrder
from app.services.cache_service import CacheService, generate_cache_key
from app.services.category_service import CategoryService
from app.services.product_service import ProductService


@pytest.fixture
def mock_db() -> MagicMock:
    return MagicMock(spec=Session)


@pytest.fixture
def sample_product() -> Product:
    now = datetime.now(timezone.utc)
    prod = Product(
        id=10,
        name="iPhone 15 Pro",
        description="Điện thoại cao cấp",
        price=Decimal("25000000.00"),
        stock=50,
        category_id=1,
        image_url="https://example.com/iphone.png",
        is_active=True,
    )
    prod.created_at = now
    prod.updated_at = now
    return prod


@pytest.fixture
def sample_category() -> Category:
    now = datetime.now(timezone.utc)
    cat = Category(id=1, name="Điện thoại", description="Danh mục")
    cat.created_at = now
    return cat


def test_generate_cache_key_deterministic_sorting():
    # Cùng tham số nhưng thứ tự truyền vào khác nhau phải sinh ra cùng một key
    key1 = generate_cache_key("product:list", page=1, page_size=10, search="phone", category_id=2)
    key2 = generate_cache_key("product:list", search="phone", category_id=2, page_size=10, page=1)
    assert key1 == key2

    # Bỏ qua giá trị None
    key_with_none = generate_cache_key("product:list", page=1, search=None)
    key_without_none = generate_cache_key("product:list", page=1)
    assert key_with_none == key_without_none

    # Tham số khác nhau sinh ra key khác nhau
    key3 = generate_cache_key("product:list", page=2, page_size=10)
    assert key1 != key3


def test_get_product_cache_aside(mock_db, sample_product):
    service = ProductService()
    service.product_repo = MagicMock()
    service.product_repo.get_by_id.return_value = sample_product

    # Lần 1: Cache miss -> query repo
    res1 = service.get_product(mock_db, 10)
    assert res1.id == 10
    assert res1.name == "iPhone 15 Pro"
    assert service.product_repo.get_by_id.call_count == 1

    # Lần 2: Cache hit -> không query repo
    res2 = service.get_product(mock_db, 10)
    assert res2.id == 10
    assert service.product_repo.get_by_id.call_count == 1


def test_list_products_paginated_cache_aside(mock_db, sample_product):
    service = ProductService()
    service.product_repo = MagicMock()
    service.product_repo.list_paginated.return_value = ([sample_product], 1)

    pagination = PaginationParams(page=1, page_size=10)
    filter_params = ProductFilter(sort_by=ProductSortBy.id, order=SortOrder.asc)

    # Lần 1: Cache miss
    res1 = service.list_products_paginated(mock_db, filter_params, pagination)
    assert isinstance(res1, PaginatedResponse)
    assert len(res1.items) == 1
    assert res1.items[0].id == 10
    assert service.product_repo.list_paginated.call_count == 1

    # Lần 2: Cache hit
    res2 = service.list_products_paginated(mock_db, filter_params, pagination)
    assert len(res2.items) == 1
    assert res2.items[0].name == "iPhone 15 Pro"
    assert service.product_repo.list_paginated.call_count == 1


def test_product_mutations_invalidate_cache(mock_db, sample_product, sample_category):
    service = ProductService()
    service.product_repo = MagicMock()
    service.product_repo.get_by_id.return_value = sample_product
    service.category_repo = MagicMock()
    service.category_repo.get_by_id.return_value = sample_category

    # Pre-populate product list và detail cache
    service.cache.set("product:list:hash1", {"items": []})
    service.cache.set("product:list:hash2", {"items": []})
    service.cache.set("product:detail:10", {"id": 10, "name": "iPhone Cũ"})

    # 1. Update product
    update_dto = ProductUpdate(
        name="iPhone 15 Pro Max",
        price=Decimal("30000000.00"),
        stock=20,
        category_id=1,
    )
    service.update_product(mock_db, 10, update_dto)
    assert service.cache.get("product:detail:10") is None
    assert service.cache.get("product:list:hash1") is None
    assert service.cache.get("product:list:hash2") is None

    # Pre-populate lại
    service.cache.set("product:list:hash1", {"items": []})
    service.cache.set("product:detail:10", {"id": 10})

    # 2. Patch product
    patch_dto = ProductPatch(stock=15)
    service.patch_product(mock_db, 10, patch_dto)
    assert service.cache.get("product:detail:10") is None
    assert service.cache.get("product:list:hash1") is None

    # Pre-populate lại
    service.cache.set("product:list:hash1", {"items": []})
    service.cache.set("product:detail:10", {"id": 10})

    # 3. Delete product
    service.delete_product(mock_db, 10)
    assert service.cache.get("product:detail:10") is None
    assert service.cache.get("product:list:hash1") is None


def test_category_mutation_cross_invalidates_product_list(mock_db, sample_category):
    cat_service = CategoryService()
    cat_service.category_repo = MagicMock()
    cat_service.category_repo.get_by_id.return_value = sample_category
    cat_service.category_repo.get_by_name.return_value = None

    # Pre-populate product list cache
    cache = CacheService()
    cache.set("product:list:abc", {"items": []})
    cache.set("category:all", [{"id": 1}])

    # Cập nhật category -> phải xóa cả cache product:list
    from app.schemas.category import CategoryUpdate
    cat_service.update_category(mock_db, 1, CategoryUpdate(name="Tên Mới"))

    assert cache.get("category:all") is None
    assert cache.get("product:list:abc") is None
