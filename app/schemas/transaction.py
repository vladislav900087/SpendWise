from pydantic import BaseModel, ConfigDict, model_validator
from app.models.transaction import TransactionType
from datetime import datetime, date

class TransactionRead(BaseModel):
    id: int
    user_id: int
    category_id: int
    amount: int
    currency: str
    type: TransactionType
    transaction_date: date
    description: str | None
    created_at: datetime
    updated_at: datetime

class TransactionCreate(BaseModel):
    category_id: int
    amount: int
    currency: str | None = None
    transaction_type: TransactionType | None = None
    transaction_date: str | None = None
    description: str | None = None

class TransactionUpdate(BaseModel):
    category_id: int | None = None
    amount: int | None = None
    currency: str | None = None
    transaction_type: TransactionType | None = None
    transaction_date: str | None = None
    description: str | None = None



