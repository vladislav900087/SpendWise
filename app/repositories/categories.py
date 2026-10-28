from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models.category import Category, CategoryType
from typing import Optional

class CategoryRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, category: Category) -> Category:

        self.db.add(category)
        self.db.commit()
        self.db.refresh(category)

        return category

    def update(self, category: Category) -> Category:

        self.db.add(category)
        self.db.commit()
        self.db.refresh(category)

        return category

    def delete(self, category: Category) -> None:

        self.db.delete(category)
        self.db.commit()

    def list_by_user(self, user_id: int, category_type: Optional[CategoryType] = None) -> list[Category]:

        statement = select(Category).where(Category.user_id == user_id).order_by(Category.created_at.desc())

        if category_type:
            statement = statement.where(Category.type == category_type)

        return list(self.db.scalars(statement))



    def get_by_id(self, category_id: int) -> Category | None:

        statement = select(Category).where(Category.id == category_id)

        return self.db.scalar(statement)



    def get_by_name_and_type(self, user_id: int, name: str, category_type: CategoryType) -> Category | None:

        statement = select(Category).where(Category.user_id == user_id, Category.name == name, Category.type == category_type)

        return self.db.scalar(statement)