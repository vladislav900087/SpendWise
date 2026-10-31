from app.repositories.transactions import TransactionRepository
from app.repositories.categories import CategoryRepository
from app.repositories.users import UsersRepository
from app.models.transaction import TransactionType, Transaction
from app.models.category import CategoryType
from utils.check_date_format import check_date_format
from datetime import date, datetime, timezone
from decimal import Decimal




class TransactionService:
    def __init__(self, repository: TransactionRepository, users_repository: UsersRepository, category_repository: CategoryRepository):

        self.repository = repository
        self.users_repository = users_repository
        self.category_repository = category_repository
    def create_transaction(self, user_id: int, category_id: int, amount: int, currency: str | None = None, transaction_type: TransactionType | None = None, transaction_date: str | None = None, description: str | None = None) -> Transaction:

        user = self.users_repository.get_by_id(user_id)
        if user is None:
            raise ValueError('User not found.')


        category = self.category_repository.get_by_id(category_id)

        if category is None or category.user_id != user.id:
            raise ValueError('Category not found.')

        transaction = Transaction(user_id=user.id, category_id=category.id)

        if transaction_type is not None:
            if category.type != transaction_type:
                raise ValueError('Transaction type should match the category type.')
            transaction.type = transaction_type
        else:
            if category.type == CategoryType.INCOME:
                transaction.type = TransactionType.INCOME
            else:
                transaction.type = TransactionType.EXPENSE

        if isinstance(amount, int) and amount > 0:
            transaction.amount = amount
        else:
            raise ValueError('Amount should be a positive integer.')




        if currency is not None:
            if len(currency) == 3 and currency in ('USD', 'EUR', 'RUB', 'KZT'):

                transaction.currency = currency
            else:
                raise ValueError('Invalid currency.')
        else:
            transaction.currency = 'USD'

        if transaction_date is not None and check_date_format(transaction_date):
            transaction.transaction_date = transaction_date
        else:
            transaction.transaction_date = date.today()

        if description is not None:
            transaction.description = description

        return self.repository.create(transaction)

    def update_transaction(self, user_id: int, transaction_id: int, category_id: int | None = None, amount: int | None = None, currency: str | None = None, transaction_type: TransactionType | None = None, transaction_date: str | None = None, description: str | None = None) -> Transaction:

        if all(arg is None for arg in (category_id, amount, currency, transaction_type, transaction_date, description)):
            raise ValueError('At least one transaction field is required to fill.')

        user = self.users_repository.get_by_id(user_id)


        if user is None:
            raise ValueError('User not found.')

        transaction = self.repository.get_by_id(transaction_id)

        if transaction is None or transaction.user_id != user.id:
            raise ValueError('Transaction not found.')


        current_category = self.category_repository.get_by_id(transaction.category_id)

        if category_id is not None:
            new_category = self.category_repository.get_by_id(category_id)
            if new_category is None:
                raise ValueError('Category not found.')
            if transaction_type is not None:
                if transaction_type != new_category.type:
                    raise ValueError('Transaction type should match the category type.')
            if new_category.type != transaction.type:
                if new_category.type == CategoryType.INCOME:
                    transaction.type = TransactionType.INCOME
                else:
                    transaction.type = TransactionType.EXPENSE
            transaction.category_id = new_category.id
            current_category = new_category



        if transaction_type is not None:
            if transaction_type != current_category.type:
                raise ValueError('Transaction type should match the category type.')
            transaction.type = transaction_type


        if currency is not None:
            if len(currency) == 3 and currency in ('USD', 'EUR', 'RUB', 'KZT'):
                transaction.currency = currency
            else:
                raise ValueError('Invalid currency.')

        if amount is not None:
            if amount > 0 and isinstance(amount, int):
                transaction.amount = amount
            else:
                raise ValueError('Amount should be a positive integer.')


        if transaction_date is not None and check_date_format(transaction_date):
            transaction.transaction_date = transaction_date

        if description is not None:
            transaction.description = description



        transaction.updated_at = datetime.now(timezone.utc)

        return self.repository.update(transaction)

    def list_transactions_by_user(self, user_id: int, date_from: date | str | None = None, date_to: date | str | None = None, category_id: int | None = None, transaction_type: str | None = None, min_amount: Decimal | None = None, max_amount: Decimal | None = None, sort_by: str = 'transaction_date', sort_order: str = 'desc', limit: int = 20, offset: int = 0) -> list[Transaction]:

        user = self.users_repository.get_by_id(user_id)

        if user is None:
            raise ValueError('User not found.')

        if isinstance(date_from, str):
            try:
                date_from = date.fromisoformat(date_from)
            except ValueError:
                raise ValueError('Invalid date_from format. Use YYYY-MM-DD.')

        if isinstance(date_to, str):
            try:
                date_to = date.fromisoformat(date_to)
            except ValueError:
                raise ValueError('Invalid date_to format. Use YYYY-MM-DD.')

        if date_from and date_to and date_from > date_to:
            raise ValueError('Invalid date range.')

        if min_amount is not None and min_amount < 0:
            raise ValueError('Minimum amount cannot be negative.')
        if max_amount is not None and max_amount < 0:
            raise ValueError('Maximum amount cannot be negative.')

        if min_amount is not None and max_amount is not None:
            if min_amount > max_amount:
                raise ValueError('Invalid amount range.')

        if transaction_type is not None and transaction_type not in (TransactionType.EXPENSE, TransactionType.INCOME):
            raise ValueError('Invalid transaction type.')

        if sort_by not in ('transaction_date', 'created_at', 'amount'):
            raise ValueError('Invalid sorting field.')

        if sort_order not in ('desc', 'asc'):
            raise ValueError('Invalid sorting order.')

        if category_id is not None:
            category = self.category_repository.get_by_id(category_id)
            if category is None or category.user_id != user.id:
                raise ValueError('Category not found.')


        return self.repository.list_by_user(user_id, date_from=date_from, date_to=date_to, category_id=category_id, transaction_type=transaction_type, min_amount=min_amount, max_amount=max_amount, sort_by=sort_by, sort_order=sort_order, limit=limit, offset=offset)

    def get_transaction_by_id(self, user_id: int, transaction_id: int) -> Transaction:
        user = self.users_repository.get_by_id(user_id)

        if user is None:
            raise ValueError('User not found.')

        transaction = self.repository.get_by_id(transaction_id)

        if transaction is None or transaction.user_id != user.id:
            raise ValueError('Transaction not found.')

        return transaction

    def delete_transaction(self, user_id: int, transaction_id: int) -> None:

        user = self.users_repository.get_by_id(user_id)

        if user is None:
            raise ValueError('User not found.')

        transaction = self.repository.get_by_id(transaction_id)

        if transaction is None or transaction.user_id != user.id:
            raise ValueError('Transaction not found.')

        self.repository.delete(transaction)






















