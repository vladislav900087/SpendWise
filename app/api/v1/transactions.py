from fastapi import Depends, HTTPException, APIRouter, status
from app.core.dependencies import get_current_user, get_transaction_service
from app.schemas.transaction import TransactionCreate, TransactionUpdate, TransactionRead
from app.models.user import User
from app.services.transactions import TransactionService

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
def list_all_transactions(current_user: User = Depends(get_current_user), service: TransactionService = Depends(get_transaction_service)):
    try:
        return service.list_transactions_by_user(user_id=current_user.id)
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

