from datetime import date
from pydantic import BaseModel, ConfigDict, Field
from app.schemas.meeting import MeetingRead

class ManagerCreate(BaseModel):
  name: str = Field(..., min_length=1, max_length=255)

class ManagerRead(BaseModel):
  model_config = ConfigDict(from_attributes=True)
  id: int
  name: str

class ManagerSchedule(BaseModel):
  manager_id: int
  date: date
  meetings: list[MeetingRead]
