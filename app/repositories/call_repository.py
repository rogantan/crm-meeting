from app.models.call import Call
from app.repositories.abstract_repository import AbstractRepository

class CallRepository(AbstractRepository):
  def __init__(self, session):
    super().__init__(model=Call, session=session)
