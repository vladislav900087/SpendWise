from pwdlib import PasswordHash


ACCESS_TOKEN_EXPIRE_MINUTES = 30
ALGORITHM = 'HS256'

password_hash = PasswordHash.recommended()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return password_hash.verify(plain_password, hashed_password)

def hash_password(password: str) -> str:
    return password_hash.hash(password)

hashed_password = hash_password('password123')
print(hashed_password)
print(verify_password('password123', hashed_password))