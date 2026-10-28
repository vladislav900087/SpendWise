from fastapi import Depends, HTTPException, status, APIRouter
from app.schemas.category import CategoryRead, CategoryUpdate, CategoryCreate, CategoryListByType
from app.core.dependencies import get_current_user, get_category_service
from app.services.categories import CategoryService
from app.models.user import User
from app.models.category import CategoryType

router = APIRouter(prefix='/categories', tags=['Categories'])

@router.post('', status_code=status.HTTP_201_CREATED, response_model=CategoryRead)
def create_category(data: CategoryCreate, current_user: User = Depends(get_current_user), service: CategoryService = Depends(get_category_service)):
    try:
        return service.create_category(user_id=current_user.id, name=data.name, category_type=data.type)

    except ValueError as exc:
        if 'not found' in str(exc):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
        elif 'already exists' in str(exc):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.get('/{category_id}', status_code=status.HTTP_200_OK, response_model=CategoryRead)
def get_category(category_id: int, current_user: User = Depends(get_current_user), service: CategoryService = Depends(get_category_service)):
    try:
        return service.get_by_id(user_id=current_user.id, category_id=category_id)
    except ValueError as exc:
        if 'not found' in str(exc):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

@router.patch('/{category_id}', status_code=status.HTTP_200_OK, response_model=CategoryRead)
def update_category(category_id: int, data: CategoryUpdate, current_user: User = Depends(get_current_user), service: CategoryService = Depends(get_category_service)):
    try:
        return service.update_category(user_id=current_user.id, category_id=category_id, name=data.name, category_type=data.type)
    except ValueError as exc:
        if 'not found' in str(exc):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
        elif 'already exists' in str(exc):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

@router.delete('/{category_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_category(category_id: int, current_user: User = Depends(get_current_user), service: CategoryService = Depends(get_category_service)):
    try:
        return service.delete_category(user_id=current_user.id, category_id=category_id)
    except ValueError as exc:
        if 'not found' in str(exc):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

@router.get('', status_code=status.HTTP_200_OK, response_model=list[CategoryRead])
def list_user_categories(current_user: User = Depends(get_current_user), service: CategoryService = Depends(get_category_service)):
    try:
        return service.list_categories(user_id=current_user.id)
    except ValueError as exc:
        if 'not found' in str(exc):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
