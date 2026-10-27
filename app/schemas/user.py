from pydantic import BaseModel, EmailStr, ConfigDict
from datetime import datetime

class UserRead(BaseModel):
    id: int
    email: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class UserCreate(BaseModel):
    email: EmailStr
    password: str



