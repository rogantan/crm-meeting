from pydantic import BaseModel, ConfigDict, Field
from app.enums.status import CompanyStatus

class CompanyCreate(BaseModel):
  name: str
  bin: str = Field(..., min_length=12, max_length=12, pattern=r"^\d{12}$")
  phone: str = Field(..., min_length=1, max_length=32)

class CompanyRead(BaseModel):
  model_config = ConfigDict(from_attributes=True)
  id: int
  name: str
  bin: str = Field(..., min_length=12, max_length=12)
  phone: str
  status: CompanyStatus

class PaginatedCompanies(BaseModel):
  items: list[CompanyRead]
  total: int
  page: int
  size: int