from app.db.session import SessionLocal
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status


from app.repositories.users import UsersRepository
from app.services.auth import AuthService, oauth2_scheme
from app.models.user import User

def get_db() -> Session:
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()

def get_users_repository(db: Session = Depends(get_db)) -> UsersRepository:
    return UsersRepository(db=db)

def get_auth_service(repository: UsersRepository = Depends(get_users_repository)) -> AuthService:
    return AuthService(repository=repository)

def get_current_user(token: str = Depends(oauth2_scheme), service: AuthService = Depends(get_auth_service)) -> User:
    try:
        return service.get_current_user(token)

    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc))





