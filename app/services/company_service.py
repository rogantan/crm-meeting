from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from app.enums.status import CompanyStatus
from app.schemas.company import CompanyCreate, CompanyRead, PaginatedCompanies
from app.repositories.company_repository import CompanyRepository

class CompanyService:
  def __init__(self, session: AsyncSession):
    self.session = session
    self.repository = CompanyRepository(session)

  async def create_company(self, payload: CompanyCreate):
    data = payload.model_dump()
    data["status"] = CompanyStatus.new
    try:
      company_new = await self.repository.insert(**data)
      await self.session.commit()
    except IntegrityError:
      await self.session.rollback()
      raise HTTPException(status_code=409, detail="Компания с таким БИН уже существует")
    return CompanyRead.model_validate(company_new)

  async def get_companies(self, status: str | None, page: int, size: int):
    if status is not None:
      try:
        CompanyStatus(status)
      except ValueError:
        raise HTTPException(status_code=422, detail="Unknown company status")
    rows, total = await self.repository.get_with_filters(status, page, size)
    items = [CompanyRead.model_validate(row) for row in rows]
    return PaginatedCompanies(items=items, total=total, page=page, size=size)

    