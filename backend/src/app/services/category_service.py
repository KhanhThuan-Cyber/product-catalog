from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.category import Category
from app.repositories.category_repository import CategoryRepository
from app.repositories.product_repository import ProductRepository
from app.schemas.category import CategoryCreate, CategoryUpdate


class CategoryService:
    def __init__(self) -> None:
        self.category_repo = CategoryRepository()
        self.product_repo = ProductRepository()

    def list_categories(self, db: Session) -> list[Category]:
        return self.category_repo.list_all(db)

    def get_category(self, db: Session, category_id: int) -> Category:
        category = self.category_repo.get_by_id(db, category_id)

        if category is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found",
            )

        return category

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
            return category
        except IntegrityError:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Could not create category due to a data conflict",
            )

    def update_category(
        self,
        db: Session,
        category_id: int,
        data: CategoryUpdate,
    ) -> Category:
        category = self.get_category(db, category_id)
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
            return category
        except IntegrityError:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Could not update category due to a data conflict",
            )

    def delete_category(self, db: Session, category_id: int) -> None:
        category = self.get_category(db, category_id)

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