from app.repositories.users import UsersRepository
from app.models.user import User
from app.core.security import hash_password, verify_password, ACCESS_TOKEN_EXPIRE_MINUTES, ALGORITHM
from datetime import datetime, timezone, timedelta
from app.core.config import settings
from fastapi.security import OAuth2PasswordBearer

SECRET_KEY = settings.secret_key
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='login')


import jwt

class AuthService:
    def __init__(self, repository: UsersRepository):
        self.repository = repository

    def create_user(self, email: str, password: str) -> User:

        existing_user = self.repository.get_by_email(email)

        if existing_user is not None:
            raise ValueError('User already exists.')

        user = User(email=email, password=hash_password(password))

        return self.repository.create(user)

    def authenticate_user(self, email: str, password: str) -> User | None:

        user = self.repository.get_by_email(email)

        if user is None:
            return None

        if not verify_password(password, user.hashed_password):
            return None

        return user

    def create_access_token(self, data: dict) -> str:

        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

        to_encode.update({'exp': expire})

        return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    def login_user(self, email: str, password: str) -> dict:

        user = self.authenticate_user(email, password)

        if user is None:
            raise ValueError('Incorrect email or password.')

        token = self.create_access_token({'sub': str(user.id), 'iat': datetime.now(timezone.utc)})

        return {'access_token': token, 'token_type': 'bearer'}

    def get_current_user(self, token: str) -> User | None:
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            user_id = payload.get('sub')
            if user_id is None:
                raise ValueError('Could not validate credentials.')

            user_id = int(user_id)

            user = self.repository.get_by_id(user_id)

            if user is None:
                raise ValueError('User does not exist.')

            return user
        except jwt.InvalidTokenError:
            raise ValueError('Invalid token.')








