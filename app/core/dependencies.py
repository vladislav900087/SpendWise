from app.db.session import SessionLocal
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status


from app.repositories.users import UsersRepository
from app.services.auth import AuthService, oauth2_scheme
from app.models.user import User

from app.repositories.categories import CategoryRepository
from app.services.categories import CategoryService

from app.repositories.transactions import TransactionRepository
from app.services.transactions import TransactionService

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

def get_category_repository(db: Session = Depends(get_db)) -> CategoryRepository:
    return CategoryRepository(db=db)

def get_category_service(users_repository: UsersRepository = Depends(get_users_repository), category_repository: CategoryRepository = Depends(get_category_repository)) -> CategoryService:
    return CategoryService(users_repository=users_repository, category_repository=category_repository)

def get_transaction_repository(db: Session = Depends(get_db)) -> TransactionRepository:
    return TransactionRepository(db=db)

def get_transaction_service(repository: TransactionRepository = Depends(get_transaction_repository), category_repository: CategoryRepository = Depends(get_category_repository), users_repository: UsersRepository = Depends(get_users_repository)) -> TransactionService:
    return TransactionService(repository=repository, category_repository=category_repository, users_repository=users_repository)









