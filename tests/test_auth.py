from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.models.user import User
from app.core.security import hash_password

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