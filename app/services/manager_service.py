from datetime import datetime, time, timedelta
from zoneinfo import ZoneInfo
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.manager_repository import ManagerRepository
from app.repositories.meeting_repository import MeetingRepository
from app.schemas.manager import ManagerCreate, ManagerRead, ManagerSchedule
from app.schemas.meeting import MeetingRead

ALMATY_TZ = ZoneInfo("Asia/Almaty")

class ManagerService:
  def __init__(self, session: AsyncSession):
    self.session = session
    self.repository = ManagerRepository(session)
    self.meeting_repository = MeetingRepository(session)

  async def create_manager(self, payload: ManagerCreate):
    manager = await self.repository.insert(**payload.model_dump())
    await self.session.commit()
    return ManagerRead.model_validate(manager)

  async def get_schedule(self, manager_id: int, day):
    manager = await self.repository.get_by_id(manager_id)
    if not manager:
      raise HTTPException(status_code=404, detail="Менеджер не найден")
    local_start = datetime.combine(day, time.min, tzinfo=ALMATY_TZ)
    local_end = local_start + timedelta(days=1)
    meetings = await self.meeting_repository.list_for_manager(manager_id, local_start, local_end)
    return ManagerSchedule(
      manager_id=manager_id,
      date=day,
      meetings=[MeetingRead.model_validate(item) for item in meetings],
    )
