from sqlalchemy import func, select
from app.enums.status import CompanyStatus
from app.models.company import Company
from app.repositories.abstract_repository import AbstractRepository

class CompanyRepository(AbstractRepository):
  def __init__(self, session):
    super().__init__(model=Company, session=session)

  async def get_with_filters(self, status: str | None, page: int, size: int):
    filters = []
    if status:
      filters.append(Company.status == CompanyStatus(status))
    count_query = select(func.count()).select_from(Company)
    query = select(Company).order_by(Company.id)
    if filters:
      count_query = count_query.where(*filters)
      query = query.where(*filters)
    total = (await self.session.execute(count_query)).scalar_one()
    result = await self.session.execute(query.offset((page - 1) * size).limit(size))
    return result.scalars().all(), total