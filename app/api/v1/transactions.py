from fastapi import Depends, HTTPException, APIRouter, status
from app.core.dependencies import get_current_user, get_transaction_service
from app.schemas.transaction import TransactionCreate, TransactionUpdate, TransactionRead, PaginatedResponse
from app.models.user import User
from app.services.transactions import TransactionService
from datetime import date
from decimal import Decimal
from fastapi import Query
from typing import Literal

router = APIRouter(prefix='/transactions', tags=['Transactions'])

@router.post('', status_code=status.HTTP_201_CREATED, response_model=TransactionRead)
def create_transaction(data: TransactionCreate, current_user: User = Depends(get_current_user), service: TransactionService = Depends(get_transaction_service)):
    try:
        return service.create_transaction(user_id=current_user.id, category_id=data.category_id, amount=data.amount, currency=data.currency, transaction_type=data.transaction_type, transaction_date=data.transaction_date, description=data.description)

    except ValueError as exc:
        if 'not found' in str(exc):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

@router.get('', status_code=status.HTTP_200_OK, response_model=list[TransactionRead])
def list_all_transactions(date_from: date | None = Query(default=None, description='Start date (YYYY-MM-DD)'), date_to: date | None = Query(default=None, description='End date (YYYY-MM-DD)'), category_id: int | None = None, transaction_type: Literal['income', 'expense'] | None = None, min_amount: Decimal | None = None, max_amount: Decimal | None = None, sort_by: Literal['transaction_date', 'created_at', 'amount'] = 'transaction_date', sort_order: Literal['desc', 'asc'] = 'desc', limit: int = Query(default=20, ge=1, le=100), offset: int = Query(default=0, ge=0), current_user: User = Depends(get_current_user), service: TransactionService = Depends(get_transaction_service)):
    try:
        items = service.list_transactions_by_user(user_id=current_user.id, date_from=date_from, date_to=date_to, category_id=category_id, transaction_type=transaction_type, min_amount=min_amount, max_amount=max_amount, sort_by=sort_by, sort_order=sort_order, limit=limit, offset=offset)
        return items
    except ValueError as exc:
        if 'not found' in str(exc):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

@router.patch('/{transaction_id}', status_code=status.HTTP_200_OK, response_model=TransactionRead)
def update_transaction(transaction_id: int, data: TransactionUpdate, current_user: User = Depends(get_current_user), service: TransactionService = Depends(get_transaction_service)):
    try:
        return service.update_transaction(user_id=current_user.id, transaction_id=transaction_id, category_id=data.category_id, amount=data.amount, currency=data.currency, transaction_type=data.transaction_type, transaction_date=data.transaction_date, description=data.description)
    except ValueError as exc:
        if 'not found' in str(exc):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

@router.get('/{transaction_id}', status_code=status.HTTP_200_OK, response_model=TransactionRead)
def get_transaction(transaction_id: int, current_user: User = Depends(get_current_user), service: TransactionService = Depends(get_transaction_service)):
    try:
        return service.get_transaction_by_id(transaction_id=transaction_id, user_id=current_user.id)

    except ValueError as exc:
        if 'not found' in str(exc):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

@router.delete('/{transaction_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_transaction(transaction_id: int, current_user: User = Depends(get_current_user), service: TransactionService = Depends(get_transaction_service)):
    try:
        return service.delete_transaction(user_id=current_user.id, transaction_id=transaction_id)
    except ValueError as exc:
        if 'not found' in str(exc):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

