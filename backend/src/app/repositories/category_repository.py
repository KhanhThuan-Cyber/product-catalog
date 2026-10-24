from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.category import Category


class CategoryRepository:
    def get_by_id(self, db: Session, category_id: int) -> Category | None:
        return db.get(Category, category_id)

    def get_by_name(self, db: Session, name: str) -> Category | None:
        statement = select(Category).where(
            func.lower(Category.name) == name.strip().lower()
        )
        return db.scalar(statement)

    def list_all(self, db: Session) -> list[Category]:
        statement = select(Category).order_by(Category.id)
        return list(db.scalars(statement).all())

    def create(self, db: Session, category: Category) -> Category:
        db.add(category)
        return category

    def delete(self, db: Session, category: Category) -> None:
        db.delete(category)