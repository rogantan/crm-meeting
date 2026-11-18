from typing import Optional
from fastapi import APIRouter, Depends, Query
from app.schemas.company import CompanyCreate
from app.api.dependencies import get_company_service
from app.services.company_service import CompanyService

router = APIRouter(prefix="/companies", tags=["Companies"])

@router.post("")
async def create_company(data: CompanyCreate, company_service: CompanyService = Depends(get_company_service)):
  return await company_service.create_company(data)

@router.get("")
async def get_companies_wuth_filters(status: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    company_service: CompanyService = Depends(get_company_service)):
  return await company_service.get_companies(status, page, size)