from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models.transaction import Transaction


class TransactionRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, transaction: Transaction) -> Transaction:
        self.db.add(transaction)
        self.db.commit()
        self.db.refresh(transaction)

        return transaction

    def get_by_id(self, transaction_id: int) -> Transaction | None:

        statement = select(Transaction).where(Transaction.id == transaction_id)

        return self.db.scalar(statement)

    def list_by_user(self, user_id: int) -> list[Transaction]:
        statement = select(Transaction).where(Transaction.user_id == user_id)

        return list(self.db.scalars(statement))

    def update(self, transaction: Transaction) -> Transaction:

        self.db.commit()
        self.db.refresh(transaction)

        return transaction

    def delete(self, transaction: Transaction) -> None:

        self.db.delete(transaction)
        self.db.commit()