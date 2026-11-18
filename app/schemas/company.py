from pydantic import BaseModel, Field
from app.enums.status import CompanyStatus

class CompanyCreate(BaseModel):
  name: str
  bin: str = Field(..., min_length=12, max_length=12)

class CompanyRead(BaseModel):
  id: int
  name: str
  bin: str = Field(..., min_length=12, max_length=12)
  status: CompanyStatus

class PaginatedCompanies(BaseModel):
  items: list[CompanyRead]
  total: int
  page: int
  size: int