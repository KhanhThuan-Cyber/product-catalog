"""Dịch vụ quản lý cache (Cache-Aside Pattern) cho ứng dụng.

Cung cấp các thao tác đọc/ghi/xóa dữ liệu cache trong Redis với:
- Hỗ trợ serialize / deserialize tự động thông qua Pydantic v2 TypeAdapter.
- Phục hồi an toàn (graceful degradation): Khi Redis lỗi hoặc dùng NoOp client,
  thao tác cache trở về no-op (get trả None coi như cache miss, không làm sập ứng dụng).
- Xóa theo tiền tố an toàn qua SCAN + pipeline DELETE (thay vì KEYS gây block server).
"""

from __future__ import annotations

import hashlib
import json
import logging
from typing import Any, TypeVar

from pydantic import TypeAdapter
from redis.exceptions import RedisError

from app.core.config import settings
from app.core.redis import NoOpRedisClient

logger = logging.getLogger(__name__)

T = TypeVar("T")


def generate_cache_key(prefix: str, **kwargs: Any) -> str:
    """Tạo cache key có tính tất định bằng cách sắp xếp tham số và băm MD5.
    
    Lọc bỏ các tham số có giá trị None để tránh phân mảnh cache giữa việc
    truyền None và không truyền tham số.
    """
    cleaned = {k: v for k, v in kwargs.items() if v is not None}
    if not cleaned:
        return prefix

    # Sắp xếp các cặp (key, value) theo key tăng dần để đảm bảo tính tất định
    sorted_items = sorted(cleaned.items(), key=lambda item: item[0])
    serialized = json.dumps(sorted_items, default=str, sort_keys=True)
    param_hash = hashlib.md5(serialized.encode("utf-8")).hexdigest()
    return f"{prefix}:{param_hash}"


class CacheService:
    """Service xử lý tầng cache Redis."""

    def __init__(self, client: Any = None) -> None:
        self._client = client

    @property
    def client(self) -> Any:
        """Lấy Redis client hiện tại (hỗ trợ lazy lookup để test có thể override)."""
        if self._client is not None:
            return self._client
        from app.core import redis as redis_module
        return redis_module.redis_client

    def _format_key(self, key: str) -> str:
        """Tạo key đầy đủ kèm prefix cấu hình nếu có."""
        prefix = settings.CACHE_KEY_PREFIX or ""
        return f"{prefix}{key}"

    @staticmethod
    def generate_cache_key(prefix: str, **kwargs: Any) -> str:
        """Helper gọi generate_cache_key từ instance hoặc class."""
        return generate_cache_key(prefix, **kwargs)

    def invalidate_product_caches(self, product_id: int | None = None) -> None:
        """Xóa toàn bộ cache danh sách sản phẩm và cache chi tiết nếu có ID.
        
        Hàm dùng chung cho cả ProductService và CategoryService khi có mutation,
        giúp tránh hardcode string prefix giữa các service.
        """
        try:
            self.delete_by_prefix("product:list:")
            if product_id is not None:
                self.delete(f"product:detail:{product_id}")
        except Exception as exc:
            logger.warning("Lỗi xóa cache sản phẩm: %s", exc)

    def get(self, key: str, schema: Any = None) -> Any:
        """Đọc dữ liệu từ cache.
        
        Args:
            key: Mã định danh cache key.
            schema: Kiểu dữ liệu / Pydantic model hoặc TypeAdapter để deserialize.
                   Nếu None, parse JSON thông thường (dict/list).
        
        Returns:
            Dữ liệu đã deserialize hoặc None nếu cache miss hoặc có lỗi xảy ra.
        """
        full_key = self._format_key(key)
        try:
            raw = self.client.get(full_key)
            if raw is None:
                logger.debug("Cache MISS: %s", full_key)
                return None

            logger.debug("Cache HIT: %s", full_key)
            if schema is None:
                return json.loads(raw)

            adapter = schema if isinstance(schema, TypeAdapter) else TypeAdapter(schema)
            return adapter.validate_json(raw)
        except Exception as exc:
            logger.warning("Lỗi đọc cache key '%s': %s (fallback cache miss)", full_key, exc)
            return None

    def set(
        self,
        key: str,
        value: Any,
        schema: Any = None,
        ttl: int | None = None,
    ) -> bool:
        """Lưu dữ liệu vào cache kèm thời gian sống (TTL).
        
        Args:
            key: Mã định danh cache key.
            value: Dữ liệu cần cache (model Pydantic, dict, list, scalar).
            schema: Kiểu dữ liệu Pydantic hoặc TypeAdapter để serialize.
            ttl: Thời gian sống (giây). Nếu None, không hết hạn.
            
        Returns:
            True nếu ghi thành công, False nếu thất bại hoặc client là NoOp.
        """
        full_key = self._format_key(key)
        try:
            if schema is not None:
                adapter = schema if isinstance(schema, TypeAdapter) else TypeAdapter(schema)
                data_str = adapter.dump_json(value).decode("utf-8")
            elif isinstance(value, (dict, list)):
                data_str = json.dumps(value, default=str)
            elif isinstance(value, str):
                data_str = value
            else:
                data_str = str(value)

            result = self.client.set(full_key, data_str, ex=ttl)
            logger.debug("Cache SET: %s (ttl=%s)", full_key, ttl)
            return bool(result)
        except Exception as exc:
            logger.warning("Lỗi ghi cache key '%s': %s", full_key, exc)
            return False

    def delete(self, key: str) -> bool:
        """Xóa một key xác định khỏi cache."""
        full_key = self._format_key(key)
        try:
            self.client.delete(full_key)
            logger.debug("Cache DELETE: %s", full_key)
            return True
        except Exception as exc:
            logger.warning("Lỗi xóa cache key '%s': %s", full_key, exc)
            return False

    def delete_by_prefix(self, prefix: str) -> int:
        """Xóa tất cả các key bắt đầu bằng prefix thông qua SCAN + Pipeline DELETE.
        
        Tránh sử dụng lệnh KEYS() làm nghẽn server Redis khi số lượng key lớn.
        """
        full_prefix = self._format_key(prefix)
        try:
            keys: list[str] = []
            for key in self.client.scan_iter(match=f"{full_prefix}*", count=100):
                keys.append(key)

            if not keys:
                return 0

            # Sử dụng pipeline để xóa theo lô, giảm RTT
            with self.client.pipeline(transaction=False) as pipe:
                for i in range(0, len(keys), 100):
                    batch = keys[i : i + 100]
                    pipe.delete(*batch)
                pipe.execute()

            logger.debug("Cache DELETE BY PREFIX '%s*': đã xóa %d keys", full_prefix, len(keys))
            return len(keys)
        except Exception as exc:
            logger.warning("Lỗi xóa cache theo prefix '%s': %s", full_prefix, exc)
            return 0


# Singleton mức module (khớp với convention chung của project)
cache_service = CacheService()
