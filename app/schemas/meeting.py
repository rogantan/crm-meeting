from datetime import datetime
from pydantic import BaseModel, ConfigDict
from app.enums.status import MeetingStatus

class MeetingCreate(BaseModel):
  company_id: int
  manager_id: int
  start_time: datetime

class MeetingUpdate(BaseModel):
  start_time: datetime | None = None
  status: MeetingStatus | None = None

class MeetingRead(BaseModel):
  model_config = ConfigDict(from_attributes=True)
  id: int
  company_id: int
  manager_id: int
  start_time: datetime
  end_time: datetime
  original_scheduled_at: datetime
  status: MeetingStatus
