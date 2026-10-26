# app/services/product_service.py
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
from app.services.base import BaseService


class ProductService(BaseService):
    def __init__(
        self,
        product_repo: ProductRepository | None = None,
        category_repo: CategoryRepository | None = None,
    ) -> None:
        self.product_repo = product_repo or ProductRepository()
        self.category_repo = category_repo or CategoryRepository()

    def get_product(self, db: Session, product_id: int) -> Product:
        product = self.product_repo.get_by_id(db, product_id)
        return self.ensure_exists(product, "Product")

    def list_products_paginated(
        self,
        db: Session,
        filter_params: ProductFilter | None = None,
        pagination: PaginationParams | None = None,
    ) -> PaginatedResponse[ProductResponse]:
        pagination = pagination or PaginationParams()

        items, total = self.product_repo.list_paginated(
            db=db,
            filter_params=filter_params,
            pagination=pagination,
        )

        return PaginatedResponse[ProductResponse].create(
            items=[ProductResponse.model_validate(p) for p in items],
            total=total,
            pagination=pagination,
        )

    def create_product(self, db: Session, data: ProductCreate) -> Product:
        category = self.category_repo.get_by_id(db, data.category_id)
        self.ensure_exists(category, "Category")

        product = Product(**data.model_dump())
        self.product_repo.create(db, product)

        self.commit_or_rollback(
            db, conflict_detail="Could not create product due to a data conflict"
        )
        db.refresh(product)
        return product

    def update_product(
        self, db: Session, product_id: int, data: ProductUpdate
    ) -> Product:
        product = self.get_product(db, product_id)

        category = self.category_repo.get_by_id(db, data.category_id)
        self.ensure_exists(category, "Category")

        self.apply_update(product, data, exclude_unset=False)

        self.commit_or_rollback(
            db, conflict_detail="Could not update product due to a data conflict"
        )
        db.refresh(product)
        return product

    def patch_product(
        self, db: Session, product_id: int, data: ProductPatch
    ) -> Product:
        product = self.get_product(db, product_id)

        if data.category_id is not None:
            category = self.category_repo.get_by_id(db, data.category_id)
            self.ensure_exists(category, "Category")

        self.apply_update(product, data, exclude_unset=True)

        self.commit_or_rollback(
            db, conflict_detail="Could not update product due to a data conflict"
        )
        db.refresh(product)
        return product

    def delete_product(self, db: Session, product_id: int) -> None:
        product = self.get_product(db, product_id)
        self.product_repo.delete(db, product)
        self.commit_or_rollback(
            db, conflict_detail="Product is referenced by another record"
        )