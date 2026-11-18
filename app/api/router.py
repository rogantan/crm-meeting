from fastapi import APIRouter
from app.api.routers.call import router as call_router
from app.api.routers.company import router as company_router
from app.api.routers.manager import router as manager_router
from app.api.routers.meeting import router as meeting_router

router = APIRouter()

router.include_router(company_router)
router.include_router(call_router)
router.include_router(meeting_router)
router.include_router(manager_router)