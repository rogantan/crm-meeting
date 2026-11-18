from fastapi import APIRouter
from app.api.routers.company import router as company_router

router = APIRouter()

router.include_router(company_router)