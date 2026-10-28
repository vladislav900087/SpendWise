from fastapi import APIRouter
from app.api.v1.auth import router as auth_router

router = APIRouter(prefix='/api/v1', tags=['API'])

router.include_router(auth_router)


