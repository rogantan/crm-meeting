from datetime import date as date_type
from fastapi import APIRouter, Depends, Query
from app.api.dependencies import get_manager_service
from app.schemas.manager import ManagerCreate
from app.services.manager_service import ManagerService

router = APIRouter(prefix="/managers", tags=["Managers"])

@router.post("")
async def create_manager(data: ManagerCreate, manager_service: ManagerService = Depends(get_manager_service)):
  return await manager_service.create_manager(data)

@router.get("/{manager_id}/schedule")
async def get_schedule(manager_id: int, date: date_type = Query(), manager_service: ManagerService = Depends(get_manager_service)):
  return await manager_service.get_schedule(manager_id, date)
