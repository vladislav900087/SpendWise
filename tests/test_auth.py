from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.models.user import User
from app.core.security import hash_password
from app.repositories.users import UsersRepository
from app.services.auth import AuthService

import pytest

def test_health_check(client: TestClient):

    response = client.get('/health')

    assert response.status_code == 200
    assert response.json() == {'status': 'ok'}

def test_db_session_isolation(db_session: Session):

    user = User(
        email='test@example.com',
        hashed_password=hash_password('some_hashed_password')

    )

    db_session.add(user)
    db_session.commit()

    db_session.refresh(user)

    saved_user = db_session.query(User).filter_by(email='test@example.com').first()

    assert saved_user is not None
    assert saved_user.email == 'test@example.com'


def test_repository_creates_user(db_session):

    repository = UsersRepository(db=db_session)

    user = User(email='user@example.com', hashed_password=hash_password('password123'))

    user = repository.create(user)

    assert user is not None
    assert user.email == 'user@example.com'

def test_repository_updates_user(db_session):

    repository = UsersRepository(db=db_session)

    user = repository.create(User(email='user@example.com', hashed_password=hash_password('password123')))

    assert user is not None
    assert user.hashed_password != 'password123'
    assert user.email == 'user@example.com'

    user.email = 'user1@example.com'

    updated_user = repository.update(user)

    assert updated_user is not None
    assert updated_user.email == 'user1@example.com'

def test_repository_gets_user_by_id(db_session):

    repository = UsersRepository(db=db_session)

    user = repository.create(User(email='test_user@example.com', hashed_password=hash_password('password123')))

    assert user is not None

    retrieved_user = repository.get_by_id(user_id=user.id)

    assert retrieved_user is not None
    assert retrieved_user.id == user.id

def test_repository_gets_by_email(db_session):

    repository = UsersRepository(db=db_session)

    user = repository.create(User(email='test_user@example.com', hashed_password=hash_password('password123')))

    assert user is not None

    retrieved_user = repository.get_by_email(email=user.email)

    assert retrieved_user is not None
    assert retrieved_user.email == user.email

def test_auth_service_creates_user(db_session):

    repository = UsersRepository(db=db_session)
    service = AuthService(repository=repository)

    user = service.create_user(email='test_user@example.com', password='password123')

    assert user is not None
    assert user.email == 'test_user@example.com'
    assert user.hashed_password != 'password123'

def test_auth_service_does_not_create_user_if_the_one_exists(db_session):

    repository = UsersRepository(db=db_session)
    service = AuthService(repository=repository)

    user = service.create_user(email='already_existing_user@example.com', password='password123')

    assert user is not None
    assert user.email == 'already_existing_user@example.com'
    assert user.hashed_password != 'password123'

    with pytest.raises(ValueError, match='User already exists.'):
        service.create_user(email='already_existing_user@example.com', password='password123')

def test_auth_service_authenticates_user(db_session):

    repository = UsersRepository(db=db_session)
    service = AuthService(repository=repository)

    user = service.create_user(email='the_user_that_should_be_authenticated@example.com', password='password123')

    assert user is not None

    authenticated_user = service.authenticate_user(email=user.email, password='password123')

    assert authenticated_user is not None
    assert authenticated_user.email == user.email
    assert authenticated_user.hashed_password != 'password123'

def test_auth_service_does_not_authenticate_user_with_invalid_email(db_session):

    repository = UsersRepository(db=db_session)
    service = AuthService(repository=repository)

    user = service.create_user(email='user_that_should_not_be_authenticated@example.com', password='password123')

    assert user is not None

    authenticated_user = service.authenticate_user(email='invalid_user_email@example.com', password='password123')

    assert authenticated_user is None

def test_auth_service_does_not_authenticate_user_with_invalid_password(db_session):

    repository = UsersRepository(db=db_session)
    service = AuthService(repository=repository)

    user = service.create_user(email='this_user_should_not_be_authenticated@example.com', password='password123')

    assert user is not None

    authenticated_user = service.authenticate_user(email=user.email, password='invalid_password123')

    assert authenticated_user is None

def test_auth_service_logins_user(db_session):

    repository = UsersRepository(db=db_session)
    service = AuthService(repository=repository)

    user = service.create_user(email='login_user@example.com', password='password123')

    assert user is not None

    access_token = service.login_user(email=user.email, password='password123')

    assert access_token is not None

    assert isinstance(access_token['access_token'], str) is True
    assert access_token['token_type'] == 'bearer'

def test_auth_service_does_not_login_user_with_invalid_email(db_session):

    repository = UsersRepository(db=db_session)
    service = AuthService(repository=repository)

    user = service.create_user(email='this_user_should_not_be_logged_in@example.com', password='password123')

    assert user is not None

    with pytest.raises(ValueError, match='Incorrect email or password.'):
        service.login_user(email='invalid_email@example.com', password='password123')

def test_auth_service_does_not_login_user_with_invalid_password(db_session):

    repository = UsersRepository(db=db_session)
    service = AuthService(repository=repository)

    user = service.create_user(email='a_user_with_invalid_password@example.com', password='password123')

    assert user is not None

    with pytest.raises(ValueError, match='Incorrect email or password.'):
        service.login_user(email=user.email, password='invalid_password123')

def test_auth_service_gets_current_user_after_login(db_session):

    repository = UsersRepository(db=db_session)

    service = AuthService(repository=repository)

    user = service.create_user(email='test_get_current_user@example.com', password='password123')

    assert user is not None

    access_token = service.login_user(email=user.email, password='password123')

    assert access_token is not None
    assert isinstance(access_token['access_token'], str) is True
    assert access_token['token_type'] == 'bearer'

    retrieved_user = service.get_current_user(token=access_token['access_token'])

    assert retrieved_user is not None
    assert retrieved_user.email == user.email
    assert retrieved_user.id == user.id
    assert retrieved_user.hashed_password != 'password123'

def test_auth_api_registers_user(client):

    response = client.post('/api/v1/auth/register', json={'email': 'test_user@example.com', 'password': 'password123'})

    assert response.status_code == 201

    assert response.json()['email'] == 'test_user@example.com'

def test_auth_api_does_not_register_the_same_user_twice(client):

    response = client.post('/api/v1/auth/register', json={"email": 'test_user@example.com', 'password': 'password123'})

    assert response.status_code == 201

    assert response.json()['email'] == 'test_user@example.com'

    duplicate_attempt_response = client.post('/api/v1/auth/register', json={'email': 'test_user@example.com', 'password': 'password123@example.com'})

    assert duplicate_attempt_response.status_code == 400

def test_auth_api_logins_registered_user(client):

    register_response = client.post('/api/v1/auth/register', json={"email": 'test_user@example.com', 'password': 'password123'})

    assert register_response.status_code == 201

    login_response = client.post('/api/v1/auth/login', data={"username": 'test_user@example.com', 'password': 'password123'})

    assert login_response.status_code == 200
    assert login_response.json()['access_token'] is not None
    assert isinstance(login_response.json()['access_token'], str) is True
    assert login_response.json()['token_type'] == 'bearer'

def test_auth_api_does_not_login_user_with_invalid_email(client):

    register_response = client.post('/api/v1/auth/register', json={"email": 'test_user@example.com', 'password': 'password123'})

    assert register_response.status_code == 201

    login_response = client.post('/api/v1/auth/login', data={'username': 'invalid_email@example.com', 'password': 'password123'})

    assert login_response.status_code == 401

def test_auth_api_does_not_login_user_with_invalid_password(client):

    register_response = client.post('/api/v1/auth/register', json={'email': 'test_user@example.com', 'password': 'password123'})

    assert register_response.status_code == 201

    login_response = client.post('/api/v1/auth/login', data={"username": 'test_user@example.com', 'password': 'invalid_password123'})

    assert login_response.status_code == 401

def test_auth_api_gets_current_user_after_login(client):

    register_response = client.post('/api/v1/auth/register', json={'email': 'test_user@example.com', 'password': 'password123'})

    assert register_response.status_code == 201

    login_response = client.post('/api/v1/auth/login', data={"username": 'test_user@example.com', 'password': 'password123'})

    assert login_response.status_code == 200

    token = login_response.json()['access_token']

    assert token is not None
    assert isinstance(token, str) is True

    get_me_response = client.get('/api/v1/auth/me', headers={'Authorization': f'Bearer {token}'})

    assert get_me_response.status_code == 200

    assert register_response.json()['id'] == get_me_response.json()['id']















