from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.company import CompanyCreate, CompanyRead, PaginatedCompanies
from app.repositories.company_repository import CompanyRepository

class CompanyService:
  def __init__(self, session: AsyncSession):
    self.session = session
    self.repository = CompanyRepository(session)

  async def create_company(self, payload: CompanyCreate):
    data = payload.model_dump()
    company_new = await self.repository.insert(**data)
    await self.session.commit()
    return CompanyRead.model_validate(company_new)

  async def get_companies(self, status: str, page: int, size: int):
    tup = await self.repository.get_with_filters(status, page, size)
    return PaginatedCompanies(items=tup[0], total=tup[1], page=page, size=size)

    