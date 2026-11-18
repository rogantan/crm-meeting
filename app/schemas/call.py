from pydantic import BaseModel, ConfigDict
from app.enums.result import CallResult

class CallCreate(BaseModel):
  company_id: int
  result: CallResult
  meeting_id: int | None = None

class CallRead(BaseModel):
  model_config = ConfigDict(from_attributes=True)
  id: int
  company_id: int
  meeting_id: int | None
  result: CallResult
