from typing import Sequence

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.product import Product
from app.repositories.base_repository import BaseRepository
from app.schemas.pagination import PaginationParams
from app.schemas.product_filter import ProductFilter


class ProductRepository(BaseRepository[Product]):
    def __init__(self) -> None:
        super().__init__(Product)

    def list_paginated(
        self,
        db: Session,
        filter_params: ProductFilter | None = None,
        pagination: PaginationParams | None = None,
    ) -> tuple[Sequence[Product], int]:
        """Lấy danh sách sản phẩm có lọc và phân trang."""
        filters = filter_params or ProductFilter()
        pagination = pagination or PaginationParams()

        statement = filters.apply(select(Product))

        return self.paginate(db, statement, pagination)

    def list_all(
        self,
        db: Session,
        filter_params: ProductFilter | None = None,
    ) -> list[Product]:
        """Lấy toàn bộ sản phẩm phù hợp với bộ lọc."""
        filters = filter_params or ProductFilter()
        statement = filters.apply(select(Product))

        return list(db.scalars(statement).all())

    def create(self, db: Session, product: Product) -> Product:
        db.add(product)
        return product

    def delete(self, db: Session, product: Product) -> None:
        db.delete(product)

    def get_by_id(self, db: Session, product_id: int) -> Product | None:
        return db.get(Product, product_id)

    def count_by_category(self, db: Session, category_id: int) -> int:
        statement = (
            select(func.count())
            .select_from(Product)
            .where(Product.category_id == category_id)
        )
        return db.scalar(statement) or 0