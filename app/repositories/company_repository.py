from app.repositories.abstract_repository import AbstractRepository
from app.models.company import Company

class CompanyRepository(AbstractRepository):
  def __init__(self, session):
    super().__init__(model=Company, session=session)

  def get_with_filters(self, status: str, page: int, size: int):
    query = self.session.query(Company)
    if status:
      query = query.filter(Company.status == status)
    total = query.count()
    items = query.offset((page - 1) * size).limit(size).all()
    return items, total