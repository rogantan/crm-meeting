from fastapi import APIRouter, Depends
from app.api.dependencies import get_call_service
from app.schemas.call import CallCreate
from app.services.call_service import CallService

router = APIRouter(prefix="/calls", tags=["Calls"])

@router.post("")
async def create_call(data: CallCreate, call_service: CallService = Depends(get_call_service)):
  return await call_service.create_call(data)
