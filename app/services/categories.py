from app.repositories.categories import CategoryRepository
from app.models.category import Category, CategoryType
from app.repositories.users import UsersRepository
from typing import Optional


class CategoryService:
    def __init__(self, category_repository: CategoryRepository, users_repository: UsersRepository):

        self.category_repository = category_repository
        self.users_repository = users_repository

    def create_category(self, user_id: int, name: str, category_type: CategoryType):

        user = self.users_repository.get_by_id(user_id)

        if user is None:
            raise ValueError('User not found.')

        existing_category = self.category_repository.get_by_name_and_type(user_id=user.id, name=name, category_type=category_type)

        if existing_category is not None:
            raise ValueError('Category with this name and type already exists for this user.')

        category = Category(user_id=user.id, name=name, type=category_type)

        return self.category_repository.create(category)

    def list_categories(self, user_id: int, category_type: Optional[CategoryType] = None) -> list[Category]:

        user = self.users_repository.get_by_id(user_id)

        if user is None:
            raise ValueError('User not found.')

        return self.category_repository.list_by_user(user_id=user.id, category_type=category_type)

    def get_by_id(self, user_id: int, category_id: int) -> Category | None:

        user = self.users_repository.get_by_id(user_id)

        if user is None:
            raise ValueError('User not found.')

        category = self.category_repository.get_by_id(category_id)

        if category is None or category.user_id != user.id:
            raise ValueError('Category not found.')

        return category

    def update_category(self, user_id: int, category_id: int,  name: str | None, category_type: CategoryType | None) -> Category | None:

        user = self.users_repository.get_by_id(user_id)

        if user is None:
            raise ValueError('User not found.')

        category = self.category_repository.get_by_id(category_id)
        if category is None or category.user_id != user.id:
             raise ValueError('Category not found.')

        if len(category.transactions) != 0:
            raise ValueError('You cannot change a category\'s type when it already has transactions.')

        existing_category = self.category_repository.get_by_name_and_type(user_id=user.id, name=name, category_type=category_type)

        if existing_category is not None:
            raise ValueError('Category with this name and type already exists for this user.')
        if name:
            category.name = name
        if category_type:
            category.type = category_type

        return self.category_repository.update(category)

    def delete_category(self, user_id: int, category_id: int) -> None:

        user = self.users_repository.get_by_id(user_id)

        if user is None:
            raise ValueError('User not found.')

        category = self.category_repository.get_by_id(category_id)

        if category is None or category.user_id != user.id:
            raise ValueError('Category not found.')

        if len(category.transactions) != 0:
            raise ValueError('You cannot delete a category that already has transactions.')

        self.category_repository.delete(category)







