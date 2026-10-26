"""Unit tests cho Commit 2 — CacheService và tầng cache Category."""

from __future__ import annotations

from datetime import datetime, timezone
from unittest.mock import MagicMock

import pytest
from sqlalchemy.orm import Session

from app.models.category import Category
from app.schemas.category import CategoryCreate, CategoryResponse, CategoryUpdate
from app.services.cache_service import CacheService
from app.services.category_service import CategoryService


@pytest.fixture
def mock_db() -> MagicMock:
    return MagicMock(spec=Session)


@pytest.fixture
def sample_category() -> Category:
    now = datetime.now(timezone.utc)
    cat = Category(id=1, name="Điện thoại", description="Danh mục điện thoại")
    cat.created_at = now
    return cat


def test_cache_service_get_set_schema(isolated_fake_redis=None):
    cache = CacheService()
    now = datetime.now(timezone.utc)
    cat_resp = CategoryResponse(id=1, name="Laptop", description="Mô tả", created_at=now)

    # Cache MISS
    assert cache.get("category:1", CategoryResponse) is None

    # Cache SET
    saved = cache.set("category:1", cat_resp, CategoryResponse, ttl=60)
    assert saved is True

    # Cache HIT
    cached = cache.get("category:1", CategoryResponse)
    assert cached is not None
    assert cached.id == 1
    assert cached.name == "Laptop"

    # Cache DELETE
    cache.delete("category:1")
    assert cache.get("category:1", CategoryResponse) is None


def test_cache_service_delete_by_prefix():
    cache = CacheService()
    cache.set("category:1", {"name": "A"})
    cache.set("category:2", {"name": "B"})
    cache.set("category:all", [{"name": "A"}, {"name": "B"}])
    cache.set("product:1", {"name": "P1"})

    deleted_count = cache.delete_by_prefix("category:")
    assert deleted_count == 3
    assert cache.get("category:1") is None
    assert cache.get("category:2") is None
    assert cache.get("category:all") is None
    # Key khác prefix không bị ảnh hưởng
    assert cache.get("product:1") is not None


def test_list_categories_cache_aside(mock_db, sample_category):
    service = CategoryService()
    service.category_repo = MagicMock()
    service.category_repo.list_all.return_value = [sample_category]

    # Lần 1: Cache MISS -> query repo
    result1 = service.list_categories(mock_db)
    assert len(result1) == 1
    assert result1[0].name == "Điện thoại"
    assert service.category_repo.list_all.call_count == 1

    # Lần 2: Cache HIT -> không query repo lần nữa
    result2 = service.list_categories(mock_db)
    assert len(result2) == 1
    assert result2[0].name == "Điện thoại"
    assert service.category_repo.list_all.call_count == 1


def test_get_category_cache_aside(mock_db, sample_category):
    service = CategoryService()
    service.category_repo = MagicMock()
    service.category_repo.get_by_id.return_value = sample_category

    # Lần 1: Cache MISS -> query repo
    result1 = service.get_category(mock_db, 1)
    assert result1.id == 1
    assert result1.name == "Điện thoại"
    assert service.category_repo.get_by_id.call_count == 1

    # Lần 2: Cache HIT -> không query repo
    result2 = service.get_category(mock_db, 1)
    assert result2.id == 1
    assert service.category_repo.get_by_id.call_count == 1


def test_create_category_invalidates_cache(mock_db, sample_category):
    service = CategoryService()
    service.category_repo = MagicMock()
    service.category_repo.get_by_name.return_value = None

    # Giả lập pre-existing cache
    service.cache.set("category:all", [{"id": 1, "name": "Cũ"}])
    assert service.cache.get("category:all") is not None

    # Tạo mới
    create_dto = CategoryCreate(name="Máy tính bảng", description="Mô tả")
    created = service.create_category(mock_db, create_dto)

    mock_db.commit.assert_called_once()
    # Cache danh sách phải bị xóa
    assert service.cache.get("category:all") is None


def test_update_category_invalidates_cache(mock_db, sample_category):
    service = CategoryService()
    service.category_repo = MagicMock()
    service.category_repo.get_by_id.return_value = sample_category
    service.category_repo.get_by_name.return_value = None

    # Pre-populate cache
    service.cache.set("category:all", [{"id": 1, "name": "Cũ"}])
    service.cache.set("category:1", {"id": 1, "name": "Cũ"})

    update_dto = CategoryUpdate(name="Điện thoại VIP", description="Mới")
    service.update_category(mock_db, 1, update_dto)

    mock_db.commit.assert_called_once()
    # Cả cache list và cache detail id=1 đều phải bị xóa
    assert service.cache.get("category:all") is None
    assert service.cache.get("category:1") is None


def test_delete_category_invalidates_cache(mock_db, sample_category):
    service = CategoryService()
    service.category_repo = MagicMock()
    service.category_repo.get_by_id.return_value = sample_category
    service.product_repo = MagicMock()
    service.product_repo.count_by_category.return_value = 0

    # Pre-populate cache
    service.cache.set("category:all", [{"id": 1, "name": "Cũ"}])
    service.cache.set("category:1", {"id": 1, "name": "Cũ"})

    service.delete_category(mock_db, 1)

    mock_db.commit.assert_called_once()
    assert service.cache.get("category:all") is None
    assert service.cache.get("category:1") is None


def test_invalidation_error_does_not_rollback_db(mock_db, sample_category):
    # Khi Redis xóa lỗi, không được làm hỏng thao tác DB đã commit
    # Tạo fake cache riêng biệt để tránh rò rỉ mock sang singleton dùng chung
    mock_cache = MagicMock(spec=CacheService)
    mock_cache.delete.side_effect = Exception("Redis connection lost")
    mock_cache.invalidate_product_caches.side_effect = Exception("Redis connection lost")

    service = CategoryService(cache=mock_cache)
    service.category_repo = MagicMock()
    service.category_repo.get_by_name.return_value = None

    create_dto = CategoryCreate(name="Phụ kiện", description="Mô tả")
    # Không raise exception
    res = service.create_category(mock_db, create_dto)
    assert res is not None
    mock_db.commit.assert_called_once()
    mock_db.rollback.assert_not_called()
