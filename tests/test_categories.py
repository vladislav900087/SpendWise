from app.repositories.categories import CategoryRepository
from app.repositories.users import UsersRepository
from app.models.category import Category, CategoryType
from app.models.user import User
from app.models.transaction import Transaction, TransactionType
from datetime import date
from app.core.security import hash_password
from app.services.categories import CategoryService
import pytest

def test_repository_creates_category(db_session):

    category_repository = CategoryRepository(db_session)
    users_repository = UsersRepository(db_session)

    user = users_repository.create(User(email='test_user@example.com', hashed_password=hash_password('password123')))
    category = category_repository.create(Category(user_id=user.id, name='Food', type=CategoryType.EXPENSE))

    assert category is not None
    assert category.user_id == user.id
    assert category.name == 'Food'
    assert category.type == CategoryType.EXPENSE
    assert len(category.transactions) == 0
    assert len(user.categories) == 1

def test_repository_updates_category(db_session):

    users_repository = UsersRepository(db_session)
    category_repository = CategoryRepository(db_session)

    user = users_repository.create(User(email='test_user@example.com', hashed_password=hash_password('password123')))
    category = category_repository.create(Category(user_id=user.id, name='Fitness', type=CategoryType.EXPENSE))

    assert category is not None
    assert category.user_id == user.id

    assert category.name == 'Fitness'

    category.name = 'Education'
    updated_category = category_repository.update(category)

    assert updated_category is not None
    assert updated_category.user_id == user.id
    assert updated_category.name == 'Education'
    assert updated_category.type == CategoryType.EXPENSE
    assert len(user.categories) == 1

def test_repository_lists_categories_by_user(db_session):

    users_repository = UsersRepository(db_session)
    category_repository = CategoryRepository(db_session)


    user = users_repository.create(User(email='test_user@example.com', hashed_password=hash_password('password123')))
    first_category = category_repository.create(Category(user_id=user.id, name='First', type=CategoryType.INCOME))
    second_category = category_repository.create(Category(user_id=user.id, name='Second', type=CategoryType.EXPENSE))

    users_categories = category_repository.list_by_user(user_id=user.id)

    assert len(users_categories) == len(user.categories)
    assert users_categories[1] == second_category
    assert users_categories[0] == first_category

def test_user_cannot_view_another_users_categories_when_addressing_to_repository(db_session):

    users_repository = UsersRepository(db_session)
    category_repository = CategoryRepository(db_session)

    first_user = users_repository.create(User(email='first_user@example.com', hashed_password=hash_password('password123')))
    second_user = users_repository.create(User(email='second_user@example.com', hashed_password=hash_password('password123')))

    for i in range(2):
        category_repository.create(Category(user_id=first_user.id, name=f'Category {i + 1}', type=CategoryType.EXPENSE))

    for i in range(2):
        category_repository.create(Category(user_id=second_user.id, name=f'Category {i + 2}', type=CategoryType.INCOME))

    first_users_categories = category_repository.list_by_user(user_id=first_user.id)
    second_users_categories = category_repository.list_by_user(user_id=second_user.id)

    assert first_users_categories[0].user_id == first_user.id
    assert second_users_categories[0].user_id == second_user.id

    assert first_users_categories[1].user_id != second_user.id
    assert second_users_categories[1].user_id != first_user.id



def test_repository_gets_category_by_its_id(db_session):

    users_repository = UsersRepository(db_session)
    category_repository = CategoryRepository(db_session)

    user = users_repository.create(User(email='test_user@example.com', hashed_password=hash_password('password123')))
    created_category = category_repository.create(Category(user_id=user.id, name='Wage', type=CategoryType.INCOME))

    assert created_category is not None
    assert created_category.user_id == user.id

    retrieved_category = category_repository.get_by_id(created_category.id)
    assert retrieved_category.id == created_category.id

def test_service_creates_category(db_session):

    users_repository = UsersRepository(db_session)
    category_repository = CategoryRepository(db_session)

    service = CategoryService(users_repository=users_repository, category_repository=category_repository)

    user = users_repository.create(User(email='test_user@example.com', hashed_password=hash_password('password123')))

    category = service.create_category(user_id=user.id, name='Food', category_type=CategoryType.EXPENSE)

    assert category is not None
    assert category.user_id == user.id
    assert category.name == 'Food'

def test_service_does_not_create_category_for_non_existent_user(db_session):

    users_repository = UsersRepository(db_session)
    category_repository = CategoryRepository(db_session)

    service = CategoryService(users_repository=users_repository, category_repository=category_repository)

    with pytest.raises(ValueError, match='User not found.'):
        service.create_category(user_id=1, name='Food', category_type=CategoryType.EXPENSE)

def test_service_does_not_create_same_category_twice(db_session):

    users_repository = UsersRepository(db_session)
    category_repository = CategoryRepository(db_session)

    service = CategoryService(users_repository=users_repository, category_repository=category_repository)

    user = users_repository.create(User(email='test_user@example.com', hashed_password=hash_password('password123')))

    category = service.create_category(user_id=user.id, name='Food', category_type=CategoryType.EXPENSE)

    assert category is not None
    assert category.user_id == user.id

    with pytest.raises(ValueError, match='Category with this name and type already exists for this user.'):
        service.create_category(user_id=user.id, name='Food', category_type=CategoryType.EXPENSE)

def test_service_can_create_same_category_twice_for_different_users(db_session):

    users_repository = UsersRepository(db_session)
    category_repository = CategoryRepository(db_session)

    service = CategoryService(users_repository=users_repository, category_repository=category_repository)

    first_user = users_repository.create(User(email='first@example.com', hashed_password=hash_password('password123')))
    second_user = users_repository.create(User(email='second@example.com', hashed_password=hash_password('password123')))

    first_user_category = service.create_category(user_id=first_user.id, name='Food', category_type=CategoryType.EXPENSE)
    second_user_category = service.create_category(user_id=second_user.id, name='Food', category_type=CategoryType.EXPENSE)

    assert first_user_category is not None
    assert first_user_category.user_id == first_user.id
    assert second_user_category is not None
    assert second_user_category.user_id == second_user.id

    assert first_user_category.name == second_user_category.name
    assert first_user_category.type == second_user_category.type

def test_service_updates_category(db_session):

    users_repository = UsersRepository(db_session)
    category_repository = CategoryRepository(db_session)

    service = CategoryService(users_repository=users_repository, category_repository=category_repository)

    user = users_repository.create(User(email='test_user@example.com', hashed_password=hash_password('password123')))

    created_category = service.create_category(user_id=user.id, name='Food', category_type=CategoryType.EXPENSE)

    updated_category = service.update_category(user_id=user.id, category_id=created_category.id, name='Salary', category_type=CategoryType.INCOME)

    assert updated_category is not None
    assert updated_category.user_id == user.id
    assert updated_category.id == created_category.id
    assert updated_category.name == 'Salary'
    assert updated_category.type == CategoryType.INCOME

def test_service_does_not_update_category_for_missing_user(db_session):

    users_repository = UsersRepository(db_session)
    category_repository = CategoryRepository(db_session)

    service = CategoryService(users_repository=users_repository, category_repository=category_repository)

    with pytest.raises(ValueError, match='User not found.'):
        service.update_category(user_id=1, category_id=1, name='Food', category_type=CategoryType.EXPENSE)

def test_service_does_not_update_missing_category(db_session):

    users_repository = UsersRepository(db_session)
    category_repository = CategoryRepository(db_session)

    service = CategoryService(users_repository=users_repository, category_repository=category_repository)

    user = users_repository.create(User(email='test_user@example.com', hashed_password=hash_password('password123')))

    with pytest.raises(ValueError, match='Category not found.'):
        service.update_category(user_id=user.id, category_id=1, name='Food', category_type=CategoryType.EXPENSE)

def test_service_does_not_update_category_that_has_transactions(db_session):

    users_repository = UsersRepository(db_session)
    category_repository = CategoryRepository(db_session)

    service = CategoryService(users_repository=users_repository, category_repository=category_repository)

    user = users_repository.create(User(email='test_user@example.com', hashed_password=hash_password('password123')))

    category = service.create_category(user_id=user.id, name='Food', category_type=CategoryType.EXPENSE)

    assert category is not None
    assert category.user_id == user.id

    transaction = Transaction(user_id=user.id, category_id=category.id, amount=1000, currency='RUB', type=TransactionType.EXPENSE, transaction_date=date.today())

    db_session.add(transaction)
    db_session.commit()
    db_session.refresh(transaction)


    assert len(category.transactions) == 1

    with pytest.raises(ValueError, match='You cannot change a category\'s type when it already has transactions.'):
        service.update_category(user_id=user.id, category_id=category.id, name='Money received', category_type=CategoryType.INCOME)

def test_service_lists_user_categories(db_session):

    users_repository = UsersRepository(db_session)
    category_repository = CategoryRepository(db_session)

    service = CategoryService(users_repository=users_repository, category_repository=category_repository)

    user = users_repository.create(User(email='test_user@example.com', hashed_password=hash_password('password123')))

    first_category = service.create_category(user_id=user.id, name='First', category_type=CategoryType.EXPENSE)

    assert first_category is not None

    second_category = service.create_category(user_id=user.id, name='Second', category_type=CategoryType.INCOME)

    assert second_category is not None

    users_categories = service.list_categories(user_id=user.id)

    assert len(users_categories) == 2
    assert users_categories[0].id == first_category.id
    assert users_categories[1].id == second_category.id

    expense_categories = service.list_categories(user_id=user.id, category_type=CategoryType.EXPENSE)
    income_categories = service.list_categories(user_id=user.id, category_type=CategoryType.INCOME)

    assert len(expense_categories) == 1
    assert len(income_categories) == 1

    assert expense_categories[0].type == CategoryType.EXPENSE
    assert income_categories[0].type == CategoryType.INCOME

def test_service_does_not_list_categories_for_missing_user(db_session):

    users_repository = UsersRepository(db_session)
    category_repository = CategoryRepository(db_session)

    service = CategoryService(users_repository=users_repository, category_repository=category_repository)

    with pytest.raises(ValueError, match='User not found.'):
        service.list_categories(user_id=1)

def test_service_gets_category_by_id(db_session):

    users_repository = UsersRepository(db_session)
    category_repository = CategoryRepository(db_session)

    service = CategoryService(users_repository=users_repository, category_repository=category_repository)

    user = users_repository.create(User(email='test_user@example.com', hashed_password=hash_password('password123')))

    created_category = service.create_category(user_id=user.id, name='Food', category_type=CategoryType.EXPENSE)

    assert created_category is not None

    retrieved_category = service.get_by_id(user_id=user.id, category_id=created_category.id)

    assert retrieved_category is not None
    assert retrieved_category.id == created_category.id

def test_service_does_not_retrieve_category_by_id_for_missing_user(db_session):

    users_repository = UsersRepository(db_session)
    category_repository = CategoryRepository(db_session)

    service = CategoryService(users_repository=users_repository, category_repository=category_repository)

    with pytest.raises(ValueError, match='User not found.'):
        service.get_by_id(user_id=1, category_id=1)

def test_service_does_not_get_missing_category_by_id(db_session):

    users_repository = UsersRepository(db_session)
    category_repository = CategoryRepository(db_session)

    service = CategoryService(users_repository=users_repository, category_repository=category_repository)

    user = users_repository.create(User(email='test_user@example.com', hashed_password=hash_password('password123')))

    with pytest.raises(ValueError, match='Category not found.'):
        service.get_by_id(user_id=user.id, category_id=1)

def test_service_deletes_category(db_session):

    users_repository = UsersRepository(db_session)
    category_repository = CategoryRepository(db_session)

    service = CategoryService(users_repository=users_repository, category_repository=category_repository)

    user = users_repository.create(User(email='test_user@example.com', hashed_password=hash_password('password123')))

    category = service.create_category(user_id=user.id, name='Food', category_type=CategoryType.EXPENSE)

    assert category is not None

    service.delete_category(user_id=user.id, category_id=category.id)

    with pytest.raises(ValueError, match='Category not found.'):
        service.get_by_id(user_id=user.id, category_id=category.id)

def test_service_does_not_delete_category_for_missing_user(db_session):

    users_repository = UsersRepository(db_session)
    category_repository = CategoryRepository(db_session)

    service = CategoryService(users_repository=users_repository, category_repository=category_repository)

    with pytest.raises(ValueError, match='User not found.'):
        service.delete_category(user_id=1, category_id=1)

def test_service_does_not_delete_missing_category(db_session):

    users_repository = UsersRepository(db_session)
    category_repository = CategoryRepository(db_session)

    service = CategoryService(users_repository=users_repository, category_repository=category_repository)

    user = users_repository.create(User(email='test_user@example.com', hashed_password=hash_password('password123')))

    with pytest.raises(ValueError, match='Category not found.'):
        service.delete_category(user_id=user.id, category_id=1)

def test_service_does_not_delete_category_that_has_transactions(db_session):

    users_repository = UsersRepository(db_session)
    category_repository = CategoryRepository(db_session)

    service = CategoryService(users_repository=users_repository, category_repository=category_repository)

    user = User(email='test_user@example.com', hashed_password=hash_password('password123'))
    user = users_repository.create(user)

    category = service.create_category(user_id=user.id, name='Food', category_type=CategoryType.EXPENSE)

    transaction = Transaction(user_id=user.id, category_id=category.id, amount=1000, currency='RUB', type=TransactionType.EXPENSE, transaction_date=date.today())

    db_session.add(transaction)
    db_session.commit()
    db_session.refresh(transaction)

    assert transaction.category_id == category.id

    with pytest.raises(ValueError, match='You cannot delete a category that already has transactions.'):
        service.delete_category(user_id=user.id, category_id=category.id)

def test_api_creates_category(client):

    register_response = client.post('/api/v1/auth/register', json={'email': 'test_user@example.com', 'password': 'password123'})

    assert register_response.status_code == 201

    login_response = client.post('/api/v1/auth/login', data={'username': 'test_user@example.com', 'password': 'password123'})

    assert login_response.status_code == 200

    access_token = login_response.json()['access_token']

    create_response = client.post('/api/v1/categories', headers={"Authorization": f'Bearer {access_token}'}, json={'name': 'Food', 'type': CategoryType.EXPENSE})

    assert create_response.status_code == 201

def test_unauthenticated_post_request_receives_401(client):

    response = client.post('/api/v1/categories')

    assert response.status_code == 401

def test_api_does_not_create_duplicate_categories(client):

    register_response = client.post('/api/v1/auth/register', json={'email': 'test_user@example.com', 'password': 'password123'})

    assert register_response.status_code == 201

    login_response = client.post('/api/v1/auth/login', data={'username': 'test_user@example.com', 'password': 'password123'})

    assert login_response.status_code == 200

    access_token = login_response.json()['access_token']

    responses = []
    for i in range(2):
        response = client.post('/api/v1/categories', headers={'Authorization': f'Bearer {access_token}'}, json={'name': 'Food', 'type': CategoryType.EXPENSE})
        responses.append(response)

    assert responses[0].status_code == 201
    assert responses[1].status_code == 409

def test_api_lists_user_categories(client):

    register_response = client.post('/api/v1/auth/register', json={"email": 'test_user@example.com', 'password': 'password123'})

    assert register_response.status_code == 201

    login_response = client.post('/api/v1/auth/login', data={"username": 'test_user@example.com', 'password': 'password123'})

    assert login_response.status_code == 200
    access_token = login_response.json()['access_token']

    payloads = [{'name': 'Food', 'type': CategoryType.EXPENSE}, {'name': 'Fitness', 'type': CategoryType.EXPENSE}]
    responses = []

    for payload in payloads:
        response = client.post('/api/v1/categories', headers={'Authorization': f'Bearer {access_token}'}, json=payload)
        responses.append(response)

    for response in responses:
        assert response.status_code == 201

    list_response = client.get('/api/v1/categories', headers={"Authorization": f'Bearer {access_token}'})

    assert list_response.status_code == 200
    assert len(list_response.json()) == 2

    assert list_response.json()[0]['id'] == responses[0].json()['id']
    assert list_response.json()[1]['id'] == responses[1].json()['id']

def test_user_cannot_list_another_users_categories(client):

    responses = []
    payloads = []
    access_tokens = []

    for i in range(2):
        response = client.post('/api/v1/auth/register', json={'email': f'test_user_{i}@example.com', 'password': 'password123'})
        responses.append(response)

    for response in responses:
        assert response.status_code == 201
        payloads.append(response.json())

    responses.clear()

    for payload in payloads:
        response = client.post('/api/v1/auth/login', data={'username': payload['email'], 'password': 'password123'})
        responses.append(response)

    for response in responses:
        assert response.status_code == 200
        access_tokens.append(response.json())

    responses.clear()



    for payload in access_tokens:
        for i in range(2):
            response = client.post('/api/v1/categories', headers={"Authorization": f'Bearer {payload['access_token']}'}, json={'name': f'category_{i}', 'type': CategoryType.EXPENSE})
            responses.append(response)

    assert len(responses) == 4



    for response in responses:
        assert response.status_code == 201

    responses.clear()

    for payload in access_tokens:
        response = client.get('/api/v1/categories', headers={'Authorization': f'Bearer {payload['access_token']}'})
        responses.append(response)

    user_ids = []

    for response in responses:
        assert response.status_code == 200
        assert len(response.json()) == 2
        user_id = response.json()[0]['user_id']
        user_ids.append(user_id)

    assert len(user_ids) == 2
    assert user_ids[0] != user_ids[1]

def test_api_gets_category_by_id(client):

    register_response = client.post('/api/v1/auth/register', json={"email": 'test_user@example.com', 'password': 'password123'})

    assert register_response.status_code == 201

    login_response = client.post('/api/v1/auth/login', data={"username": 'test_user@example.com', 'password': 'password123'})

    assert login_response.status_code == 200

    token = login_response.json()['access_token']

    create_response = client.post('/api/v1/categories', headers={'Authorization': f'Bearer {token}'}, json={'name': 'Salary', 'type': CategoryType.INCOME})

    assert create_response.status_code == 201
    category_id = create_response.json()['id']

    get_response = client.get(f'/api/v1/categories/{category_id}', headers={"Authorization": f'Bearer {token}'})

    assert get_response.status_code == 200
    assert get_response.json()['name'] == 'Salary'
    assert get_response.json()['type'] == CategoryType.INCOME

def test_user_cannot_get_another_users_category_by_id(client):

    emails = ['first_user@example.com', 'second_user@example.com']

    for email in emails:
        response = client.post('/api/v1/auth/register', json={'email': email, 'password': 'password123'})
        assert response.status_code == 201

    tokens = []

    for email in emails:
        response = client.post('/api/v1/auth/login', data={"username": email, 'password': 'password123'})
        assert response.status_code == 200
        token = response.json()['access_token']
        tokens.append(token)

    category_ids = []

    for token in tokens:
        response = client.post('/api/v1/categories', headers={'Authorization': f'Bearer {token}'}, json={'name': 'Food', 'type': CategoryType.EXPENSE})
        assert response.status_code == 201
        category_id = response.json()['id']
        user_id = response.json()['user_id']
        category_ids.append({'user_id': user_id, 'category_id': category_id})

    get_first_user_id_response = client.get('/api/v1/auth/me', headers={"Authorization": f'Bearer {tokens[0]}'})

    assert get_first_user_id_response.status_code == 200
    first_user_id = get_first_user_id_response.json()['id']

    assert category_ids[0]['user_id'] == first_user_id

    get_second_user_id_response = client.get('/api/v1/auth/me', headers={"Authorization": f'Bearer {tokens[1]}'})

    assert get_second_user_id_response.status_code == 200
    second_user_id = get_second_user_id_response.json()['id']

    assert category_ids[1]['user_id'] == second_user_id

    get_first_user_category_response = client.get(f'/api/v1/categories/{category_ids[0]['category_id']}', headers={"Authorization": f'Bearer {tokens[0]}'})
    assert get_first_user_category_response.status_code == 200
    category_id = get_first_user_category_response.json()['id']

    assert category_ids[0]['category_id'] == category_id

    get_second_user_category_response = client.get(f'/api/v1/categories/{category_ids[1]['category_id']}', headers={'Authorization': f'Bearer {tokens[1]}'})

    assert get_second_user_category_response.status_code == 200

    category_id = get_second_user_category_response.json()['id']
    assert category_ids[1]['category_id'] == category_id

    first_user_cannot_get_second_users_category_response = client.get(f'/api/v1/categories/{category_ids[1]['category_id']}', headers={'Authorization': f'Bearer {tokens[0]}'})

    assert first_user_cannot_get_second_users_category_response.status_code == 404

    second_user_cannot_get_first_users_category_response = client.get(f'/api/v1/categories/{category_ids[0]['category_id']}', headers={'Authorization': f'Bearer {tokens[1]}'})

    assert second_user_cannot_get_first_users_category_response.status_code == 404

def test_user_cannot_get_missing_category_by_id(client):

    register_response = client.post('/api/v1/auth/register', json={"email": 'test_user@example.com', 'password': 'password123'})

    assert register_response.status_code == 201

    login_response = client.post('/api/v1/auth/login', data={"username": 'test_user@example.com', 'password': 'password123'})

    assert login_response.status_code == 200

    access_token = login_response.json()['access_token']

def test_unauthorized_user_cannot_get_category_by_id(client):

    response = client.get('/api/v1/categories/999999')

    assert response.status_code == 401

def test_api_updates_category_by_id(client):

    register_response = client.post('/api/v1/auth/register', json={"email": 'test_user@example.com', 'password': 'password123'})

    assert register_response.status_code == 201

    login_response = client.post('/api/v1/auth/login', data={"username": 'test_user@example.com', 'password': 'password123'})

    assert login_response.status_code == 200
    access_token = login_response.json()['access_token']

    create_response = client.post('/api/v1/categories', headers={'Authorization': f'Bearer {access_token}'}, json={'name': 'Food', 'type': CategoryType.EXPENSE})

    assert create_response.status_code == 201

    category_id = create_response.json()['id']

    update_response = client.patch(f'/api/v1/categories/{category_id}', headers={"Authorization": f'Bearer {access_token}'}, json={'name': 'Top Up', 'type': CategoryType.INCOME})

    assert update_response.status_code == 200
    assert update_response.json()['name'] == 'Top Up'
    assert update_response.json()['type'] == CategoryType.INCOME
    assert update_response.json()['id'] == category_id

def test_user_cannot_update_another_users_category_by_id(client):

    emails = ['first_user@example.com', 'second_user@example.com']

    user_data = []

    for email in emails:
        register_response = client.post('/api/v1/auth/register', json={'email': email, 'password': 'password123'})

        assert register_response.status_code == 201

        login_response = client.post('/api/v1/auth/login', data={'username': email, 'password': 'password123'})


        assert login_response.status_code == 200

        access_token = login_response.json()['access_token']

        payload = {'email': email, 'user_id': register_response.json()['id'], 'access_token': access_token}

        user_data.append(payload)

    first_user_get_response = client.get('/api/v1/auth/me', headers={'Authorization': f'Bearer {user_data[0]['access_token']}'})

    assert first_user_get_response.status_code == 200
    assert first_user_get_response.json()['id'] == user_data[0]['user_id']
    assert first_user_get_response.json()['email'] == user_data[0]['email']

    second_user_get_response = client.get('/api/v1/auth/me', headers={"Authorization": f'Bearer {user_data[1]['access_token']}'})

    assert second_user_get_response.status_code == 200
    assert second_user_get_response.json()['id'] == user_data[1]['user_id']
    assert second_user_get_response.json()['email'] == user_data[1]['email']

    for user in user_data:
        create_response = client.post('/api/v1/categories', headers={"Authorization": f'Bearer {user['access_token']}'}, json={"name": f'{user['email']}\'s category', 'type': CategoryType.EXPENSE})

        assert create_response.status_code == 201
        category_id = create_response.json()['id']

        user['category'] = {'category_id': category_id, 'category_name': create_response.json()['name']}

    assert user_data[0]['category'] is not None

    first_user_gets_ones_category = client.get(f'/api/v1/categories/{user_data[0]['category']['category_id']}', headers={'Authorization': f'Bearer {user_data[0]['access_token']}'})

    assert first_user_gets_ones_category.status_code == 200
    assert first_user_gets_ones_category.json()['id'] == user_data[0]['category']['category_id']
    assert first_user_gets_ones_category.json()['name'] == user_data[0]['category']['category_name']

    second_user_gets_ones_category = client.get(f'/api/v1/categories/{user_data[1]['category']['category_id']}', headers={"Authorization": f'Bearer {user_data[1]['access_token']}'})

    assert second_user_gets_ones_category.status_code == 200

    assert second_user_gets_ones_category.json()['id'] == user_data[1]['category']['category_id']
    assert second_user_gets_ones_category.json()['user_id'] == user_data[1]['user_id']
    assert second_user_gets_ones_category.json()['name'] == user_data[1]['category']['category_name']

    first_user_cannot_update_second_users_category_response = client.patch(f'/api/v1/categories/{user_data[1]['category']['category_id']}', headers={"Authorization": f'Bearer {user_data[0]['access_token']}'}, json={'name': 'Now it\'s my category', 'type': CategoryType.INCOME})


    assert first_user_cannot_update_second_users_category_response.status_code == 404

    second_user_cannot_update_first_users_category_response = client.patch(f'/api/v1/categories/{user_data[0]['category']['category_id']}', headers={"Authorization": f'Bearer {user_data[1]['access_token']}'}, json={"name": 'Now it\'s my category', 'type': CategoryType.INCOME})

    assert second_user_cannot_update_first_users_category_response.status_code == 404

def test_user_cannot_update_missing_category_by_id(client):

    register_response = client.post('/api/v1/auth/register', json={"email": 'test_user@example.com', 'password': 'password123'})

    assert register_response.status_code == 201

    login_response = client.post('/api/v1/auth/login', data={"username": 'test_user@example.com', 'password': 'password123'})

    assert login_response.status_code == 200

    access_token = login_response.json()['access_token']

    update_attempt_response = client.patch('/api/v1/categories/999999', json={'name': 'Top Up', 'type': CategoryType.INCOME}, headers={'Authorization': f'Bearer {access_token}'})

    assert update_attempt_response.status_code == 404

def test_user_cannot_set_already_existing_category_name_and_type_while_updating_category(client):

    register_response = client.post('/api/v1/auth/register', json={"email": 'test_user@example.com', 'password': 'password123'})

    assert register_response.status_code == 201

    login_response = client.post('/api/v1/auth/login', data={"username": 'test_user@example.com', 'password': 'password123'})

    assert login_response.status_code == 200

    access_token = login_response.json()['access_token']

    first_create_response = client.post('/api/v1/categories', headers={'Authorization': f'Bearer {access_token}'}, json={'name': 'Top Up', 'type': CategoryType.INCOME})

    assert first_create_response.status_code == 201

    second_create_response = client.post('/api/v1/categories', headers={'Authorization': f'Bearer {access_token}'}, json={'name': 'Fitness', 'type': CategoryType.EXPENSE})

    assert second_create_response.status_code == 201

    second_category_id = second_create_response.json()['id']

    update_attempt_response = client.patch(f'/api/v1/categories/{second_category_id}', headers={"Authorization": f'Bearer {access_token}'}, json={"name": 'Top Up', 'type': CategoryType.INCOME})

    assert update_attempt_response.status_code == 409

def test_user_cannot_update_category_that_has_transactions(client, db_session):

    register_response = client.post('/api/v1/auth/register', json={'email': 'test_user@example.com', 'password': 'password123'})

    assert register_response.status_code == 201

    login_response = client.post('/api/v1/auth/login', data={"username": 'test_user@example.com', 'password': 'password123'})

    assert login_response.status_code == 200
    access_token = login_response.json()['access_token']

    create_response = client.post('/api/v1/categories', headers={'Authorization': f'Bearer {access_token}'}, json={"name": 'Top Up', 'type': CategoryType.INCOME})

    assert create_response.status_code == 201

    user_id = register_response.json()['id']
    category_id = create_response.json()['id']

    transaction = Transaction(user_id=user_id, category_id=category_id, amount=10000, type=TransactionType.INCOME, transaction_date=date.today())

    db_session.add(transaction)
    db_session.commit()
    db_session.refresh(transaction)

    update_attempt_response = client.patch(f'/api/v1/categories/{category_id}', headers={'Authorization': f'Bearer {access_token}'}, json={'name': 'Groceries', 'type': CategoryType.EXPENSE})

    assert update_attempt_response.status_code == 400

def test_unauthenticated_user_cannot_update_category(client):

    update_attempt_response = client.patch('/api/v1/categories/999999')

    assert update_attempt_response.status_code == 401

def test_api_deletes_category(client):

    register_response = client.post('/api/v1/auth/register', json={"email": 'test_user@example.com', 'password': 'password123'})

    assert register_response.status_code == 201

    login_response = client.post('/api/v1/auth/login', data={"username": 'test_user@example.com', 'password': 'password123'})

    assert login_response.status_code == 200

    access_token = login_response.json()['access_token']

    create_response = client.post('/api/v1/categories', headers={'Authorization': f'Bearer {access_token}'}, json={"name": 'Groceries', 'type': CategoryType.EXPENSE})

    assert create_response.status_code == 201

    category_id = create_response.json()['id']

    delete_response = client.delete(f'/api/v1/categories/{category_id}', headers={'Authorization': f'Bearer {access_token}'})

    assert delete_response.status_code == 204

def test_user_cannot_delete_another_users_category(client):

    emails = ['first_user@example.com', 'second_user@example.com']
    user_data = []

    for email in emails:
        register_response = client.post('/api/v1/auth/register', json={"email": email, 'password': 'password123'})
        assert register_response.status_code == 201

        user_id = register_response.json()['id']


        login_response = client.post('/api/v1/auth/login', data={"username": email, 'password': 'password123'})

        assert login_response.status_code == 200

        access_token = login_response.json()['access_token']

        user = {'email': email, 'user_id': user_id, 'access_token': access_token}
        user_data.append(user)

    for user in user_data:
        create_response = client.post('/api/v1/categories', headers={'Authorization': f'Bearer {user['access_token']}'}, json={"name": f'{user['email']}\'s category', 'type': CategoryType.EXPENSE})
        assert create_response.status_code == 201

        category_id = create_response.json()['id']

        user['category_id'] = category_id

    first_user_cannot_delete_second_users_category = client.delete(f'/api/v1/categories/{user_data[1]['category_id']}', headers={'Authorization': f'Bearer {user_data[0]['access_token']}'})

    assert first_user_cannot_delete_second_users_category.status_code == 404

    second_user_cannot_delete_first_users_category = client.delete(f'/api/v1/categories/{user_data[0]['category_id']}', headers={"Authorization": f'Bearer {user_data[1]['access_token']}'})

    assert second_user_cannot_delete_first_users_category.status_code == 404

def test_user_cannot_delete_category_that_has_transactions(client, db_session):

    register_response = client.post('/api/v1/auth/register', json={"email": 'test_user@example.com', 'password': 'password123'})

    assert register_response.status_code == 201

    login_response = client.post('/api/v1/auth/login', data={"username": 'test_user@example.com', 'password': 'password123'})

    assert login_response.status_code == 200

    access_token = login_response.json()['access_token']

    create_response = client.post('/api/v1/categories', headers={"Authorization": f'Bearer {access_token}'}, json={'name': 'Groceries', 'type': CategoryType.EXPENSE})

    assert create_response.status_code == 201

    category_id = create_response.json()['id']

    transaction = Transaction(user_id=register_response.json()['id'], category_id=category_id, amount=1000, type=TransactionType.EXPENSE)

    db_session.add(transaction)
    db_session.commit()
    db_session.refresh(transaction)

    delete_attempt_response = client.delete(f'/api/v1/categories/{category_id}', headers={"Authorization": f'Bearer {access_token}'})

    assert delete_attempt_response.status_code == 400

def test_user_cannot_delete_missing_category(client):

    register_response = client.post('/api/v1/auth/register', json={"email": 'test_user@example.com', 'password': 'password123'})

    assert register_response.status_code == 201

    login_response = client.post('/api/v1/auth/login', data={"username": 'test_user@example.com', 'password': 'password123'})

    assert login_response.status_code == 200

    access_token = login_response.json()['access_token']

    delete_response = client.delete('/api/v1/categories/999999', headers={"Authorization": f'Bearer {access_token}'})

    assert delete_response.status_code == 404

def test_unauthenticated_user_cannot_delete_category(client):

    delete_attempt_response = client.delete('/api/v1/categories/999999')

    assert delete_attempt_response.status_code == 401













































































