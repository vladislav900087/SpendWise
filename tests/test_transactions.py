from app.repositories.transactions import TransactionRepository
from app.repositories.categories import CategoryRepository
from app.repositories.users import UsersRepository
from app.models.transaction import Transaction, TransactionType
from app.models.category import Category, CategoryType
from app.models.user import User
from app.core.security import hash_password
from app.services.transactions import TransactionService
import pytest
from datetime import date, datetime, timezone
import uuid

# useful test functions

def login(client):


    register_response = client.post('/api/v1/auth/register', json={'email': f'test_user_{uuid.uuid4().hex[:8]}@example.com', 'password': 'password123'})

    assert register_response.status_code == 201

    user_email = register_response.json()['email']

    login_response = client.post('/api/v1/auth/login', data={"username": user_email, 'password': 'password123'})

    assert login_response.status_code == 200

    access_token = login_response.json()['access_token']

    return access_token

def create_category(client, token: str, category_type: CategoryType | None = None):

    uid = uuid.uuid4().hex[:8]
    response = client.post('/api/v1/categories', json={"name": f'test_category_{uid}'}, headers={'Authorization': f'Bearer {token}'})

    assert response.status_code == 201

    if category_type is not None:
        update_response = client.patch(f'/api/v1/categories/{response.json()['id']}', headers={'Authorization': f'Bearer {token}'}, json={'type': category_type})
        assert update_response.status_code == 200

    return response.json()['id']

def create_transaction(client, token: str, transaction_type: TransactionType | None = None):

    category_id = create_category(client, token)

    standard_type = TransactionType.INCOME
    if transaction_type is not None:
        standard_type = transaction_type

    response = client.post('/api/v1/transactions', headers={'Authorization': f'Bearer {token}'}, json={"category_id": category_id, 'amount': 100, 'transaction_type': standard_type})

    assert response.status_code == 201
    return response.json()['id']


# test repository
def test_create_transaction(db_session):
    repository = TransactionRepository(db_session)
    category_repository = CategoryRepository(db_session)
    users_repository = UsersRepository(db_session)

    user = users_repository.create(User(email='test_user@example.com', hashed_password=hash_password('password123')))
    category = category_repository.create(Category(name='test_category', type=CategoryType.EXPENSE, user_id=user.id))

    transaction = repository.create(Transaction(user_id=user.id, category_id=category.id, amount=100, type=TransactionType.EXPENSE))

    assert transaction is not None
    assert transaction.user_id == user.id
    assert transaction.category_id == category.id

def test_get_transaction_by_id(db_session):

    repository = TransactionRepository(db_session)
    category_repository = CategoryRepository(db_session)
    users_repository = UsersRepository(db_session)

    user = users_repository.create(User(email='test_user@example.com', hashed_password=hash_password('password123')))
    category = category_repository.create(Category(name='test_category', type=CategoryType.EXPENSE, user_id=user.id))

    transaction = Transaction(user_id=user.id, category_id=category.id, amount=100)
    repository.create(transaction)

    retrieved_transaction = repository.get_by_id(transaction.id)

    assert retrieved_transaction is not None
    assert retrieved_transaction.id == transaction.id

def test_update_transaction(db_session):

    repository = TransactionRepository(db_session)
    category_repository = CategoryRepository(db_session)
    users_repository = UsersRepository(db_session)

    user = users_repository.create(User(email='test_user@example.com', hashed_password=hash_password('password123')))
    category = category_repository.create(Category(name='test_category', user_id=user.id))
    transaction = repository.create(Transaction(user_id=user.id, category_id=category.id, amount=100))

    assert transaction.type == TransactionType.INCOME

    transaction.type = TransactionType.EXPENSE
    transaction.amount = 200

    updated_transaction = repository.update(transaction)

    assert updated_transaction.type == TransactionType.EXPENSE
    assert updated_transaction.amount == 200

def test_list_transactions_by_user(db_session):

    repository = TransactionRepository(db_session)
    category_repository = CategoryRepository(db_session)
    users_repository = UsersRepository(db_session)

    user = users_repository.create(User(email='test_user@example.com', hashed_password=hash_password('password123')))
    category = category_repository.create(Category(name='test_category', user_id=user.id))

    for i in range(2):
        repository.create(Transaction(user_id=user.id, category_id=category.id, amount=100))

    users_transactions = repository.list_by_user(user.id)

    assert len(users_transactions) == 2

    for transaction in users_transactions:
        assert transaction.user_id == user.id
        assert transaction.category_id == category.id

def test_delete_transaction(db_session):

    repository = TransactionRepository(db_session)

    category_repository = CategoryRepository(db_session)
    users_repository = UsersRepository(db_session)

    user = users_repository.create(User(email='test_user@example.com', hashed_password=hash_password('password123')))
    category = category_repository.create(Category(name='test_category', user_id=user.id))
    transaction = repository.create(Transaction(user_id=user.id, category_id=category.id, amount=100))

    repository.delete(transaction)

    deleted_transaction = repository.get_by_id(transaction.id)

    assert deleted_transaction is None

# test service

def test_service_creates_transaction(db_session):

    repository = TransactionRepository(db_session)
    category_repository = CategoryRepository(db_session)
    users_repository = UsersRepository(db_session)

    service = TransactionService(repository=repository, category_repository=category_repository, users_repository=users_repository)

    user = repository.create(User(email='test_user@example.com', hashed_password=hash_password('password123')))

    category = category_repository.create(Category(name='test_category', type=CategoryType.EXPENSE, user_id=user.id))

    transaction = service.create_transaction(user_id=user.id, category_id=category.id, amount=100, currency='USD')

    assert transaction is not None
    assert transaction.type == category.type

def test_service_does_not_create_transaction_for_missing_user(db_session):

    repository = TransactionRepository(db_session)
    category_repository = CategoryRepository(db_session)
    users_repository = UsersRepository(db_session)

    service = TransactionService(repository=repository, category_repository=category_repository, users_repository=users_repository)

    with pytest.raises(ValueError, match='User not found.'):
        service.create_transaction(user_id=999999, category_id=999999, amount=100)

def test_service_creates_transaction_with_non_default_entered_by_user_parameters(db_session):

    repository = TransactionRepository(db_session)
    category_repository = CategoryRepository(db_session)
    users_repository = UsersRepository(db_session)

    service = TransactionService(repository=repository, category_repository=category_repository, users_repository=users_repository)

    user = users_repository.create(User(email='test_user@example.com', hashed_password=hash_password('password123')))
    category = category_repository.create(Category(name='test_category', user_id=user.id, type=CategoryType.EXPENSE))

    transaction = service.create_transaction(user_id=user.id, category_id=category.id, amount=100, currency='RUB', transaction_date='1984-04-04', transaction_type=TransactionType.EXPENSE, description='Some description')



    assert transaction is not None
    assert transaction.currency == 'RUB'
    assert transaction.transaction_date.strftime('%Y-%m-%d') == '1984-04-04'
    assert transaction.type == TransactionType.EXPENSE
    assert transaction.description == 'Some description'

def test_service_creates_transaction_with_default_parameters(db_session):

    repository = TransactionRepository(db_session)
    category_repository = CategoryRepository(db_session)
    users_repository = UsersRepository(db_session)

    service = TransactionService(repository=repository, category_repository=category_repository, users_repository=users_repository)

    user = users_repository.create(User(email='test_user@example.com', hashed_password=hash_password('password123')))
    category = category_repository.create(Category(name='test_category', type=CategoryType.EXPENSE, user_id=user.id))


    transaction = service.create_transaction(user_id=user.id, category_id=category.id, amount=100)

    assert transaction is not None
    assert transaction.currency == 'USD'
    assert transaction.type == TransactionType.EXPENSE
    assert transaction.transaction_date == date.today()
    assert transaction.description is None

def test_service_does_not_create_transaction_for_missing_category(db_session):

    repository = TransactionRepository(db_session)
    category_repository = CategoryRepository(db_session)
    users_repository = UsersRepository(db_session)

    service = TransactionService(repository=repository, category_repository=category_repository, users_repository=users_repository)

    user = users_repository.create(User(email='test_user@example.com', hashed_password=hash_password('password123')))

    with pytest.raises(ValueError, match='Category not found.'):
        service.create_transaction(user_id=user.id, category_id=999999, amount=100)

def test_service_does_not_create_transaction_if_transaction_type_and_category_type_is_different(db_session):

    repository = TransactionRepository(db_session)
    users_repository = UsersRepository(db_session)
    category_repository = CategoryRepository(db_session)

    service = TransactionService(repository=repository, category_repository=category_repository, users_repository=users_repository)

    user = users_repository.create(User(email='test_user@example.com', hashed_password=hash_password('password123')))
    category = category_repository.create(Category(name='test_category', type=CategoryType.INCOME, user_id=user.id))

    assert category.type == CategoryType.INCOME

    with pytest.raises(ValueError, match='Transaction type should match the category type.'):
        service.create_transaction(user_id=user.id, category_id=category.id, amount=100, transaction_type=TransactionType.EXPENSE)

def test_service_does_not_create_transaction_with_negative_amount(db_session):

    repository = TransactionRepository(db_session)

    category_repository = CategoryRepository(db_session)
    users_repository = UsersRepository(db_session)

    service = TransactionService(repository=repository, category_repository=category_repository, users_repository=users_repository)

    user = users_repository.create(User(email='test_user@example.com', hashed_password=hash_password('password123')))

    category = category_repository.create(Category(name='test_category', user_id=user.id))

    with pytest.raises(ValueError, match='Amount should be a positive integer.'):
        service.create_transaction(user_id=user.id, category_id=category.id, amount=-1)

def test_service_does_not_create_transaction_with_invalid_currency(db_session):

    repository = TransactionRepository(db_session)

    users_repository = UsersRepository(db_session)
    category_repository = CategoryRepository(db_session)

    service = TransactionService(repository=repository, category_repository=category_repository, users_repository=users_repository)

    user = users_repository.create(User(email='test_user@example.com', hashed_password=hash_password('password123')))

    category = category_repository.create(Category(name='test_category', user_id=user.id))

    with pytest.raises(ValueError, match='Invalid currency.'):
        service.create_transaction(user_id=user.id, category_id=category.id, amount=100, currency='USSD')

def test_service_does_not_create_transaction_with_invalid_date_format(db_session):

    repository = TransactionRepository(db_session)

    category_repository = CategoryRepository(db_session)
    users_repository = UsersRepository(db_session)

    service = TransactionService(repository=repository, category_repository=category_repository, users_repository=users_repository)

    user = users_repository.create(User(email='test_user@example.com', hashed_password=hash_password('password123')))
    category = category_repository.create(Category(name='test_category', user_id=user.id))

    transaction = service.create_transaction(user_id=user.id, category_id=category.id, amount=100, transaction_date='01-09-1939')

    assert transaction.transaction_date == date.today()

def test_service_updates_transaction(db_session):

    repository = TransactionRepository(db_session)

    category_repository = CategoryRepository(db_session)
    users_repository = UsersRepository(db_session)

    service = TransactionService(repository=repository, category_repository=category_repository, users_repository=users_repository)

    user = users_repository.create(User(email='test_user@example.com', hashed_password=hash_password('password123')))
    category = category_repository.create(Category(name='test_category', user_id=user.id))

    transaction = service.create_transaction(user_id=user.id, category_id=category.id, amount=100)

    assert transaction is not None
    assert transaction.type == TransactionType.INCOME
    assert transaction.transaction_date == date.today()
    assert transaction.currency == 'USD'

    another_category = category_repository.create(Category(name='another_category', user_id=user.id, type=CategoryType.EXPENSE))

    updated_transaction = service.update_transaction(user_id=user.id, transaction_id=transaction.id, category_id=another_category.id, amount=1000, transaction_type=TransactionType.EXPENSE, transaction_date='2022-02-24', currency='EUR', description='A description')

    assert updated_transaction is not None
    assert updated_transaction.type == TransactionType.EXPENSE
    assert updated_transaction.transaction_date.strftime('%Y-%m-%d') == '2022-02-24'
    assert updated_transaction.currency == 'EUR'
    assert updated_transaction.description == 'A description'
    assert updated_transaction.amount == 1000

def test_service_does_not_update_transaction_when_all_fields_are_none(db_session):

    repository = TransactionRepository(db_session)

    category_repository = CategoryRepository(db_session)
    users_repository = UsersRepository(db_session)

    service = TransactionService(repository=repository, category_repository=category_repository, users_repository=users_repository)

    user = users_repository.create(User(email='test_user@example.com', hashed_password=hash_password('password123')))
    category = category_repository.create(Category(name='test_category', user_id=user.id))

    transaction = service.create_transaction(user_id=user.id, category_id=category.id, amount=100)

    assert transaction is not None
    assert transaction.type == TransactionType.INCOME

    with pytest.raises(ValueError, match='At least one transaction field is required to fill.'):
        service.update_transaction(user_id=user.id, transaction_id=transaction.id)

def test_service_does_not_update_transaction_for_missing_user(db_session):

    repository = TransactionRepository(db_session)

    users_repository = UsersRepository(db_session)
    category_repository = CategoryRepository(db_session)

    service = TransactionService(repository=repository, category_repository=category_repository, users_repository=users_repository)

    with pytest.raises(ValueError, match='User not found.'):
        service.update_transaction(user_id=999999, transaction_id=999999, category_id=999999)

def test_service_does_not_update_missing_transaction(db_session):

    repository = TransactionRepository(db_session)

    category_repository = CategoryRepository(db_session)
    users_repository = UsersRepository(db_session)

    service = TransactionService(repository=repository, category_repository=category_repository, users_repository=users_repository)

    user = users_repository.create(User(email='test_user@example.com', hashed_password=hash_password('password123')))

    with pytest.raises(ValueError, match='Transaction not found.'):
        service.update_transaction(user_id=user.id, transaction_id=999999, category_id=999999)

def test_service_does_not_update_transaction_if_transaction_type_and_category_type_are_different(db_session):

    repository = TransactionRepository(db_session)

    category_repository = CategoryRepository(db_session)
    users_repository = UsersRepository(db_session)

    service = TransactionService(repository=repository, category_repository=category_repository, users_repository=users_repository)

    user = users_repository.create(User(email='test_user@example.com', hashed_password=hash_password('password123')))
    category = category_repository.create(Category(name='test_category', user_id=user.id))

    transaction = service.create_transaction(user_id=user.id, category_id=category.id, amount=100)

    assert transaction is not None
    assert transaction.type == TransactionType.INCOME

    with pytest.raises(ValueError, match='Transaction type should match the category type.'):
        service.update_transaction(user_id=user.id, transaction_id=transaction.id, transaction_type=TransactionType.EXPENSE)

def test_service_does_not_update_transaction_with_invalid_currency_amount_and_transaction_date(db_session):

    repository = TransactionRepository(db_session)

    category_repository = CategoryRepository(db_session)
    users_repository = UsersRepository(db_session)

    service = TransactionService(repository=repository, category_repository=category_repository, users_repository=users_repository)

    user = users_repository.create(User(email='test_user@example.com', hashed_password=hash_password('password123')))
    category = category_repository.create(Category(name='test_category', user_id=user.id))

    transaction = service.create_transaction(user_id=user.id, category_id=category.id, amount=100)

    assert transaction is not None
    assert transaction.type == TransactionType.INCOME
    assert transaction.currency == 'USD'

    with pytest.raises(ValueError, match='Invalid currency.'):
        service.update_transaction(user_id=user.id, transaction_id=transaction.id, currency='invalid')

    with pytest.raises(ValueError, match='Amount should be a positive integer.'):
        service.update_transaction(user_id=user.id, transaction_id=transaction.id, amount=-1)

    invalid_date_format_transaction = service.update_transaction(user_id=user.id, transaction_id=transaction.id, transaction_date='04-04-1984')

    assert invalid_date_format_transaction.transaction_date == date.today()

    assert invalid_date_format_transaction.updated_at is not None


def test_service_lists_transactions_by_user(db_session):

    repository = TransactionRepository(db_session)

    users_repository = UsersRepository(db_session)
    category_repository = CategoryRepository(db_session)

    service = TransactionService(repository=repository, category_repository=category_repository, users_repository=users_repository)

    emails = ['first_user@example.com', 'second_user@example.com']

    user_data = []
    transactions_by_user = []

    for email in emails:
        user = users_repository.create(User(email=email, hashed_password=hash_password('password123')))
        user = {'user_id': user.id, 'email': user.email}

        user_data.append(user)

    for user in user_data:
        for i in range(2):
            category = category_repository.create(Category(name=f'test_category_{user['email']}{i + 1}', user_id=user['user_id']))
            transaction = service.create_transaction(user_id=user['user_id'], category_id=category.id, amount=100)
            user['category'] = category
            user['transaction'] = transaction

            assert category.user_id == user['user_id']
            assert transaction.user_id == user['user_id']

            assert transaction.category_id == user['category'].id

    for user in user_data:
        transactions = service.list_transactions_by_user(user_id=user['user_id'])
        user_transactions = {'user_id': user['user_id'], 'transactions': transactions}
        transactions_by_user.append(user_transactions)

    assert len(transactions_by_user) == 2
    for user in transactions_by_user:
        assert len(user['transactions']) == 2
        for transaction in user['transactions']:
            assert transaction.user_id == user['user_id']
            for data in user_data:
                if data['user_id'] == user['user_id']:
                    if transaction.category_id == data['category'].id:
                        assert transaction.category_id == data['category'].id
                    if transaction.id == data['transaction'].id:
                        assert transaction.id == data['transaction'].id

def test_service_gets_transaction_by_id(db_session):

    repository = TransactionRepository(db_session)

    category_repository = CategoryRepository(db_session)
    users_repository = UsersRepository(db_session)

    service = TransactionService(repository=repository, category_repository=category_repository, users_repository=users_repository)

    user = users_repository.create(User(email='test_user@example.com', hashed_password=hash_password('password123')))
    category = category_repository.create(Category(name='test_category', user_id=user.id))

    transaction = service.create_transaction(user_id=user.id, category_id=category.id, amount=100)

    assert transaction is not None

    retrieved_transaction = service.get_transaction_by_id(transaction_id=transaction.id, user_id=user.id)

    assert retrieved_transaction.id == transaction.id
    assert retrieved_transaction.user_id == user.id
    assert retrieved_transaction.category_id == category.id

def test_service_does_not_get_transaction_for_missing_user(db_session):

    repository = TransactionRepository(db_session)

    category_repository = CategoryRepository(db_session)
    users_repository = UsersRepository(db_session)

    service = TransactionService(repository=repository, category_repository=category_repository, users_repository=users_repository)

    with pytest.raises(ValueError, match='User not found.'):
        service.get_transaction_by_id(transaction_id=999999, user_id=999999)

def test_service_does_not_list_transactions_for_missing_user(db_session):

    repository = TransactionRepository(db_session)

    category_repository = CategoryRepository(db_session)
    users_repository = UsersRepository(db_session)

    service = TransactionService(repository=repository, category_repository=category_repository, users_repository=users_repository)

    with pytest.raises(ValueError, match='User not found.'):
        service.list_transactions_by_user(user_id=999999)

def test_service_does_not_get_missing_transaction_by_id(db_session):

    repository = TransactionRepository(db_session)

    category_repository = CategoryRepository(db_session)
    users_repository = UsersRepository(db_session)

    service = TransactionService(repository=repository, category_repository=category_repository, users_repository=users_repository)

    user = users_repository.create(User(email='test_user@example.com', hashed_password=hash_password('password123')))

    with pytest.raises(ValueError, match='Transaction not found.'):
        service.get_transaction_by_id(user_id=user.id, transaction_id=999999)

def test_service_deletes_transaction(db_session):

    repository = TransactionRepository(db_session)

    category_repository = CategoryRepository(db_session)
    users_repository = UsersRepository(db_session)

    service = TransactionService(repository=repository, category_repository=category_repository, users_repository=users_repository)

    user = users_repository.create(User(email='test_user@example.com', hashed_password=hash_password('password123')))

    category = category_repository.create(Category(name='test_category', user_id=user.id))

    transaction = service.create_transaction(user_id=user.id, category_id=category.id, amount=100)

    assert transaction is not None

    service.delete_transaction(transaction_id=transaction.id, user_id=user.id)

    deleted_transaction = repository.get_by_id(transaction_id=transaction.id)

    assert deleted_transaction is None

def test_service_does_not_delete_transaction_for_missing_user(db_session):

    repository = TransactionRepository(db_session)

    category_repository = CategoryRepository(db_session)
    users_repository = UsersRepository(db_session)

    service = TransactionService(repository=repository, category_repository=category_repository, users_repository=users_repository)

    with pytest.raises(ValueError, match='User not found.'):
        service.delete_transaction(user_id=999999, transaction_id=999999)

def test_service_does_not_delete_missing_transaction(db_session):

    repository = TransactionRepository(db_session)

    category_repository = CategoryRepository(db_session)
    users_repository = UsersRepository(db_session)

    service = TransactionService(repository=repository, category_repository=category_repository, users_repository=users_repository)

    user = users_repository.create(User(email='test_user@example.com', hashed_password=hash_password('password123')))

    with pytest.raises(ValueError, match='Transaction not found.'):
        service.delete_transaction(user_id=user.id, transaction_id=999999)

# test api
def test_api_creates_transaction(client):

    register_response = client.post('/api/v1/auth/register', json={"email": 'test_user@example.com', 'password': 'password123'})

    assert register_response.status_code == 201

    login_response = client.post('/api/v1/auth/login', data={"username": 'test_user@example.com', 'password': 'password123'})

    assert login_response.status_code == 200

    access_token = login_response.json()['access_token']

    assert isinstance(access_token, str) is True

    create_category_response = client.post('/api/v1/categories', headers={"Authorization": f'Bearer {access_token}'}, json={'name': 'test_category'})


    assert create_category_response.status_code == 201

    create_transaction_response = client.post('/api/v1/transactions', headers={"Authorization": f'Bearer {access_token}'}, json={"category_id": create_category_response.json()['id'], 'amount': 100})

    assert create_transaction_response.status_code == 201
    assert create_transaction_response.json()['amount'] == 100
    assert create_transaction_response.json()['type'] == TransactionType.INCOME
    assert create_transaction_response.json()['currency'] == 'USD'
    assert create_transaction_response.json()['transaction_date'] == date.today().strftime('%Y-%m-%d')

def test_api_does_not_create_transaction_for_missing_category(client):

    register_response = client.post('/api/v1/auth/register', json={'email': 'test_user@example.com', 'password': 'password123'})

    assert register_response.status_code == 201

    login_response = client.post('api/v1/auth/login', data={'username': 'test_user@example.com', 'password': 'password123'})

    assert login_response.status_code == 200

    access_token = login_response.json()['access_token']

    create_transaction_attempt = client.post('/api/v1/transactions', headers={"Authorization": f'Bearer {access_token}'}, json={"category_id": 999999, 'amount': 100})

    assert create_transaction_attempt.status_code == 404

def test_api_does_not_create_transaction_if_its_type_differs_from_category_type(client):

    register_response = client.post('/api/v1/auth/register', json={'email': 'test_user@example.com', 'password': 'password123'})

    assert register_response.status_code == 201

    login_response = client.post('/api/v1/auth/login', data={'username': 'test_user@example.com', 'password': 'password123'})

    assert login_response.status_code == 200

    access_token = login_response.json()['access_token']

    create_category_response = client.post('/api/v1/categories', json={'name': 'test_category'}, headers={"Authorization": f'Bearer {access_token}'})

    assert create_category_response.status_code == 201
    assert create_category_response.json()['type'] == CategoryType.INCOME

    create_transaction_attempt_response = client.post('/api/v1/transactions', headers={"Authorization": f'Bearer {access_token}'}, json={'category_id': create_category_response.json()['id'], 'amount': 100, 'transaction_type': TransactionType.EXPENSE})

    assert create_transaction_attempt_response.status_code == 400

def test_api_does_not_create_transaction_with_invalid_amount_currency_and_date(client):

    access_token = login(client)
    category_id = create_category(client, token=access_token)

    assert isinstance(access_token, str) is True
    assert isinstance(category_id, int) is True

    create_transaction_with_negative_amount_response = client.post('/api/v1/transactions', headers={'Authorization': f'Bearer {access_token}'}, json={'amount': -100, 'category_id': category_id})

    assert create_transaction_with_negative_amount_response.status_code == 400

    create_transaction_with_invalid_currency_response = client.post('/api/v1/transactions', headers={'Authorization': f'Bearer {access_token}'}, json={'amount': 100, 'category_id': category_id, 'currency': 'USSD'})

    assert create_transaction_with_invalid_currency_response.status_code == 400

    create_transaction_with_invalid_date_format = client.post('/api/v1/transactions', headers={"Authorization": f'Bearer {access_token}'}, json={"amount": 200, 'category_id': category_id, 'transaction_date': '04-04-1984'})

    assert create_transaction_with_invalid_date_format.status_code == 201

    assert create_transaction_with_invalid_date_format.json()['transaction_date'] == date.today().strftime('%Y-%m-%d')

def test_api_updates_transaction(client):
    token = login(client)
    transaction_id = create_transaction(client, token=token)

    assert isinstance(transaction_id, int) is True

    update_response = client.patch(f'/api/v1/transactions/{transaction_id}', headers={'Authorization': f'Bearer {token}'}, json={'amount': 2000, 'currency': 'EUR', 'transaction_date': '1984-04-04'})

    assert update_response.status_code == 200
    assert update_response.json()['amount'] == 2000
    assert update_response.json()['currency'] == 'EUR'
    assert update_response.json()['transaction_date'] == '1984-04-04'

def test_api_does_not_update_transaction_if_new_category_type_does_not_match_transaction_type(client):

    token = login(client)

    category_id = create_category(client, token=token, category_type=CategoryType.EXPENSE)

    assert isinstance(category_id, int) is True

    transaction_id = create_transaction(client, token=token)

    assert isinstance(transaction_id, int) is True

    update_attempt_response = client.patch(f'/api/v1/transactions/{transaction_id}', headers={"Authorization": f'Bearer {token}'}, json={'category_id': category_id, 'transaction_type': TransactionType.INCOME})

    assert update_attempt_response.status_code == 400

def test_api_deals_with_all_remaining_negative_scenarios_while_updating_transaction(client, db_session):

    token = login(client)
    transaction_id = create_transaction(client, token=token)

    repository = TransactionRepository(db_session)
    category_repository = CategoryRepository(db_session)
    transaction = repository.get_by_id(transaction_id)


    assert transaction.type == TransactionType.INCOME

    new_category_id = create_category(client, token=token, category_type=CategoryType.EXPENSE)

    new_category = category_repository.get_by_id(new_category_id)
    assert new_category.type == TransactionType.EXPENSE

    # test dealing with category-transaction type mismatch

    type_mismatch_update_response = client.patch(f'/api/v1/transactions/{transaction_id}', headers={"Authorization": f'Bearer {token}'}, json={"category_id": new_category_id})

    assert type_mismatch_update_response.status_code == 200
    assert type_mismatch_update_response.json()['type'] == TransactionType.EXPENSE
    assert type_mismatch_update_response.json()['category_id'] == new_category_id

    # test dealing with invalid currency
    invalid_currency_update_attempt_response = client.patch(f'/api/v1/transactions/{transaction_id}', headers={"Authorization": f'Bearer {token}'}, json={"currency": 'USSD'})

    assert invalid_currency_update_attempt_response.status_code == 400

    # test dealing with missing category

    missing_category_update_attempt_response = client.patch(f'/api/v1/transactions/{transaction_id}', headers={"Authorization": f'Bearer {token}'}, json={'category_id': 999999})

    assert missing_category_update_attempt_response.status_code == 404

    # test dealing with negative amount

    negative_amount_update_attempt_response = client.patch(f'/api/v1/transactions/{transaction_id}', headers={"Authorization": f'Bearer {token}'}, json={'amount': -100})

    assert negative_amount_update_attempt_response.status_code == 400

    # test dealing with invalid date format
    invalid_date_update_response = client.patch(f'/api/v1/transactions/{transaction_id}', headers={"Authorization": f'Bearer {token}'}, json={'transaction_date': '04-041984'})

    assert invalid_date_update_response.status_code == 200
    assert invalid_date_update_response.json()['transaction_date'] == date.today().strftime('%Y-%m-%d')


def test_api_lists_gets_deletes_transactions_and_deals_with_all_negative_scenarios(client, db_session):


    users = []
    repository = TransactionRepository(db_session)
    for i in range(2):
        token = login(client)
        get_response = client.get('/api/v1/auth/me', headers={'Authorization': f'Bearer {token}'})
        assert get_response.status_code == 200
        user_id = get_response.json()['id']
        users.append({'user_id': user_id, 'access_token': token})

    for user in users:
        for i in range(2):
            transaction_id = create_transaction(client, token=user['access_token'])
            transaction = repository.get_by_id(transaction_id)
            assert transaction.user_id == user['user_id']

            list_response = client.get('/api/v1/transactions', headers={"Authorization": f'Bearer {user['access_token']}'})
            assert list_response.status_code == 200
            user['transactions'] = list_response.json()

            for transaction in user['transactions']:
                assert transaction['user_id'] == user['user_id']

    assert users[0]['transactions'][0]['user_id'] != users[1]['transactions'][0]['user_id']
    # GET /{transaction_id} tests
    first_user_cannot_get_second_users_transaction = client.get(f'/api/v1/transactions/{users[1]['transactions'][0]['id']}', headers={'Authorization': f'Bearer {users[0]['access_token']}'})
    assert first_user_cannot_get_second_users_transaction.status_code == 404

    second_user_cannot_get_first_users_transaction = client.get(f'/api/v1/transactions/{users[0]['transactions'][0]['id']}', headers={"Authorization": f'Bearer {users[1]['access_token']}'})
    assert second_user_cannot_get_first_users_transaction.status_code == 404

    first_user_can_get_his_transaction = client.get(f'/api/v1/transactions/{users[0]['transactions'][0]['id']}', headers={"Authorization": f'Bearer {users[0]['access_token']}'})

    assert first_user_can_get_his_transaction.status_code == 200
    assert first_user_can_get_his_transaction.json()['id'] == users[0]['transactions'][0]['id']

    second_user_can_get_ones_transaction = client.get(f'/api/v1/transactions/{users[1]['transactions'][0]['id']}', headers={"Authorization": f'Bearer {users[1]['access_token']}'})

    assert second_user_can_get_ones_transaction.status_code == 200
    assert second_user_can_get_ones_transaction.json()['id'] == users[1]['transactions'][0]['id']

    # test DELETE {transaction_id}

    first_user_cannot_delete_second_users_transaction = client.delete(f'/api/v1/transactions/{users[1]['transactions'][0]['id']}', headers={"Authorization": f'Bearer {users[0]['access_token']}'})

    assert first_user_cannot_delete_second_users_transaction.status_code == 404

    second_user_cannot_delete_first_users_transaction = client.delete(f'/api/v1/transactions{users[0]['transactions'][0]['id']}', headers={"Authorization": f'Bearer {users[1]['access_token']}'})
    assert second_user_cannot_delete_first_users_transaction.status_code == 404

    first_user_can_delete_ones_own_transaction = client.delete(f'/api/v1/transactions/{users[0]['transactions'][0]['id']}', headers={'Authorization': f'Bearer {users[0]['access_token']}'})

    assert first_user_can_delete_ones_own_transaction.status_code == 204

    second_user_can_delete_ones_own_transaction = client.delete(f'/api/v1/transactions/{users[1]['transactions'][0]['id']}', headers={"Authorization": f'Bearer {users[1]['access_token']}'})

    assert second_user_can_delete_ones_own_transaction.status_code == 204

    first_users_transactions = client.get('/api/v1/transactions', headers={'Authorization': f'Bearer {users[0]['access_token']}'})
    assert first_users_transactions.status_code == 200
    assert len(first_users_transactions.json()) == 1

    second_users_transactions = client.get('/api/v1/transactions', headers={'Authorization': f'Bearer {users[1]['access_token']}'})

    assert second_users_transactions.status_code == 200
    assert len(second_users_transactions.json()) == 1

def test_unauthenticated_api_request_gets_401(client):

    all_requests = []

    create_response = client.post('/api/v1/transactions')
    all_requests.append(create_response)
    update_response = client.patch('/api/v1/transactions/999999')
    all_requests.append(update_response)
    list_response = client.get('/api/v1/transactions')
    all_requests.append(list_response)
    get_response = client.get('/api/v1/transactions/999999')
    all_requests.append(get_response)
    delete_response = client.delete('/api/v1/transactions/999999')
    all_requests.append(delete_response)

    for response in all_requests:
        assert response.status_code == 401






















































