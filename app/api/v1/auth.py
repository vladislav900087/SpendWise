from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from app.core.dependencies import get_current_user, get_auth_service
from app.services.auth import AuthService
from app.schemas.user import UserRead, UserCreate
from app.schemas.auth import Token
from app.models.user import User


router = APIRouter(prefix='/auth', tags=['Authentication'])

@router.post('/login', status_code=status.HTTP_200_OK, response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), auth_service: AuthService = Depends(get_auth_service)):
    try:
        return auth_service.login_user(email=form_data.username, password=form_data.password)

    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc))

@router.post('/register', status_code=status.HTTP_201_CREATED, response_model=UserRead)
def register(data: UserCreate, auth_service: AuthService = Depends(get_auth_service)):
    try:
        return auth_service.create_user(email=data.email, password=data.password)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))

@router.get('/me', status_code=status.HTTP_200_OK, response_model=UserRead)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user


