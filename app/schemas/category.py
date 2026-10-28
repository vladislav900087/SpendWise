from pydantic import BaseModel, ConfigDict
from app.models.category import CategoryType
from datetime import datetime

class CategoryRead(BaseModel):

    id: int
    user_id: int
    name: str
    type: CategoryType
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class CategoryCreate(BaseModel):
    name: str
    type: CategoryType

class CategoryUpdate(BaseModel):
    name: str
    type: CategoryType

class CategoryListByType(BaseModel):
    type: CategoryType | None



