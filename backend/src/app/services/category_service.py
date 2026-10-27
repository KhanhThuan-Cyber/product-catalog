import logging
from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.category import Category
from app.repositories.category_repository import CategoryRepository
from app.repositories.product_repository import ProductRepository
from app.schemas.category import CategoryCreate, CategoryResponse, CategoryUpdate
from app.services.cache_service import CacheService, cache_service

logger = logging.getLogger(__name__)


class CategoryService:
    def __init__(self, cache: CacheService | None = None) -> None:
        self.category_repo = CategoryRepository()
        self.product_repo = ProductRepository()
        self.cache = cache or cache_service

    def _invalidate_cache(self, category_id: int | None = None) -> None:
        """Xóa cache danh mục an toàn sau khi commit DB thành công.
        
        Đồng thời kích hoạt xóa cache danh sách sản phẩm (cross-invalidation)
        thông qua hàm chung của cache_service để tránh coupling cứng.
        Lỗi xảy ra tại bước invalidation cache không được làm ảnh hưởng
        hoặc rollback transaction DB đã commit.
        """
        try:
            self.cache.delete("category:all")
            if category_id is not None:
                self.cache.delete(f"category:{category_id}")
            self.cache.invalidate_product_caches()
        except Exception as exc:
            logger.warning("Lỗi khi xóa cache category: %s", exc)

    def list_categories(self, db: Session) -> list[CategoryResponse]:
        cache_key = "category:all"
        cached = self.cache.get(cache_key, list[CategoryResponse])
        if cached is not None:
            return cached

        categories = self.category_repo.list_all(db)
        result = [CategoryResponse.model_validate(c) for c in categories]
        self.cache.set(cache_key, result, list[CategoryResponse], ttl=settings.CACHE_TTL_CATEGORY)
        return result

    def get_category(self, db: Session, category_id: int) -> CategoryResponse:
        cache_key = f"category:{category_id}"
        cached = self.cache.get(cache_key, CategoryResponse)
        if cached is not None:
            return cached

        category = self.category_repo.get_by_id(db, category_id)
        if category is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found",
            )

        result = CategoryResponse.model_validate(category)
        self.cache.set(cache_key, result, CategoryResponse, ttl=settings.CACHE_TTL_CATEGORY)
        return result

    def create_category(
        self,
        db: Session,
        data: CategoryCreate,
    ) -> Category:
        name = data.name.strip()

        if self.category_repo.get_by_name(db, name):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Category name already exists",
            )

        category = Category(
            name=name,
            description=data.description,
        )

        try:
            self.category_repo.create(db, category)
            db.commit()
            db.refresh(category)
        except IntegrityError:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Could not create category due to a data conflict",
            )

        # Xóa cache ngay sau khi commit DB thành công
        self._invalidate_cache(category.id)
        return category

    def update_category(
        self,
        db: Session,
        category_id: int,
        data: CategoryUpdate,
    ) -> Category:
        category = self.category_repo.get_by_id(db, category_id)
        if category is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found",
            )

        name = data.name.strip()
        existing = self.category_repo.get_by_name(db, name)
        if existing is not None and existing.id != category_id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Category name already exists",
            )

        category.name = name
        category.description = data.description

        try:
            db.commit()
            db.refresh(category)
        except IntegrityError:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Could not update category due to a data conflict",
            )

        # Xóa cache ngay sau khi commit DB thành công
        self._invalidate_cache(category.id)
        return category

    def delete_category(self, db: Session, category_id: int) -> None:
        category = self.category_repo.get_by_id(db, category_id)
        if category is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found",
            )

        if self.product_repo.count_by_category(db, category_id) > 0:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Cannot delete a category that contains products",
            )

        try:
            self.category_repo.delete(db, category)
            db.commit()
        except IntegrityError:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Category is referenced by another record",
            )

        # Xóa cache ngay sau khi commit DB thành công
        self._invalidate_cache(category_id)
