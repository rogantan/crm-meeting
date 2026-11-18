from app.models.manager import Manager
from app.repositories.abstract_repository import AbstractRepository

class ManagerRepository(AbstractRepository):
  def __init__(self, session):
    super().__init__(model=Manager, session=session)
