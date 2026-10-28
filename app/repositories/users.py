from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models.user import User

class UsersRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, user: User) -> User:

        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)

        return user

    def get_by_id(self, user_id: int) -> User:

        statement = select(User).where(User.id == user_id)

        return self.db.scalar(statement)

    def get_by_email(self, email: str) -> User:

        statement = select(User).where(User.email == email)

        return self.db.scalar(statement)


    def update(self, user: User) -> User:

        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)

        return user

    def delete(self, user: User) -> None:

        self.db.delete(user)
        self.db.commit()