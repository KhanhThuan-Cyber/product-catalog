from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.product import Product
from app.repositories.category_repository import CategoryRepository
from app.repositories.product_repository import ProductRepository
from app.schemas.pagination import PaginatedResponse, PaginationParams
from app.schemas.product import (
    ProductCreate,
    ProductPatch,
    ProductResponse,
    ProductUpdate,
)
from app.schemas.product_filter import ProductFilter


class ProductService:
    def __init__(self) -> None:
        self.product_repo = ProductRepository()
        self.category_repo = CategoryRepository()

    def list_products_paginated(
        self,
        db: Session,
        filter_params: ProductFilter | None = None,
        pagination: PaginationParams | None = None,
    ) -> PaginatedResponse[ProductResponse]:
        """Lấy danh sách sản phẩm phân trang, có hỗ trợ tìm kiếm, lọc và sắp xếp."""
        pagination = pagination or PaginationParams()

        if filter_params is not None:
            if (
                filter_params.min_price is not None
                and filter_params.max_price is not None
                and filter_params.min_price > filter_params.max_price
            ):
                raise HTTPException(
                    status_code=400,
                    detail="min_price cannot be greater than max_price",
                )

        items, total = self.product_repo.list_paginated(
            db=db,
            filter_params=filter_params,
            pagination=pagination,
        )

        return PaginatedResponse[ProductResponse].create(
            items=[ProductResponse.model_validate(p) for p in items],
            total=total,
            page=pagination,
        )

    def list_product(
        self,
        db: Session,
        filter_params: ProductFilter | None = None,
        search: str | None = None,
    ) -> list[Product]:
        """Lấy danh sách sản phẩm không phân trang (dùng cho các trường hợp đặc thù)."""
        if filter_params is not None:
            if (
                filter_params.min_price is not None
                and filter_params.max_price is not None
                and filter_params.min_price > filter_params.max_price
            ):
                raise HTTPException(
                    status_code=400,
                    detail="min_price cannot be greater than max_price",
                )
        return self.product_repo.list_all(db, filter_params=filter_params, search=search)

    def get_product(self, db: Session, product_id: int) -> Product:
        product = self.product_repo.get_by_id(db, product_id)

        if product is None:
            raise HTTPException(
                status_code=404,
                detail="Product not found",
            )
        return product

    def create_product(self, db: Session, data: ProductCreate) -> Product:
        if not self.category_repo.get_by_id(db, data.category_id):
            raise HTTPException(404, "Category not found")

        product = Product(**data.model_dump())

        try:
            self.product_repo.create(db, product)
            db.commit()
            db.refresh(product)
            return product
        except Exception:
            db.rollback()
            raise

    def update_product(
        self, db: Session, product_id: int, data: ProductUpdate
    ) -> Product:
        product = self.get_product(db, product_id)

        if not self.category_repo.get_by_id(db, data.category_id):
            raise HTTPException(404, "Category not found")

        for key, value in data.model_dump().items():
            setattr(product, key, value)

        try:
            db.commit()
            db.refresh(product)
            return product
        except Exception:
            db.rollback()
            raise

    def patch_product(
        self, db: Session, product_id: int, data: ProductPatch
    ) -> Product:
        product = self.get_product(db, product_id)

        for key, value in data.model_dump(exclude_unset=True).items():
            setattr(product, key, value)

        try:
            db.commit()
            db.refresh(product)
            return product
        except Exception:
            db.rollback()
            raise

    def delete_product(self, db: Session, product_id: int) -> None:
        product = self.get_product(db, product_id)

        try:
            self.product_repo.delete(db, product)
            db.commit()
        except Exception:
            db.rollback()
            raise
