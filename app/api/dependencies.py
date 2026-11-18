from app.services.company_service import CompanyService
from app.repositories.company_repository import CompanyRepository
from fastapi import Depends
from app.db.db_postgres import get_session
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import settings


def get_company_service(session: AsyncSession = Depends(get_session)):
  return CompanyService(session)