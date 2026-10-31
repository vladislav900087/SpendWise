from sqlalchemy import select, func
from sqlalchemy.orm import Session
from app.models.transaction import Transaction, TransactionType



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

    def list_by_user(self, user_id: int, date_from=None, date_to=None, category_id=None, transaction_type=None, min_amount=None, max_amount=None, sort_by='transaction_date', sort_order='desc', limit: int = 20, offset: int = 0) -> list[Transaction]:
        statement = select(Transaction).where(Transaction.user_id == user_id)
        if date_from is not None:
            statement = statement.where(Transaction.transaction_date >= date_from)
        if date_to is not None:
            statement = statement.where(Transaction.transaction_date <= date_to)

        if category_id is not None:
            statement = statement.where(Transaction.category_id == category_id)

        if transaction_type is not None:
            statement = statement.where(Transaction.type == transaction_type)

        if min_amount is not None:
            statement = statement.where(Transaction.amount >= min_amount)
        if max_amount is not None:
            statement = statement.where(Transaction.amount <= max_amount)

        # total count
        count_statement = select(func.count()).select_from(statement.subquery())
        total_count = self.db.scalar(count_statement)


        sort_column = getattr(Transaction, sort_by)

        if sort_order == 'desc':
            statement = statement.order_by(sort_column.desc(), Transaction.id.desc())
        else:
            statement = statement.order_by(sort_column.asc(), Transaction.id.asc())

        if limit <= 0 or limit > 100:
            raise ValueError('Limit must be between 1 and 100')

        if offset < 0:
            raise ValueError('Offset cannot be negative')

        items = list(self.db.scalars(statement.limit(limit).offset(offset)))
        return items

    def update(self, transaction: Transaction) -> Transaction:

        self.db.commit()
        self.db.refresh(transaction)

        return transaction

    def delete(self, transaction: Transaction) -> None:

        self.db.delete(transaction)
        self.db.commit()