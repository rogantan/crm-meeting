from datetime import datetime, time, timedelta, timezone
from zoneinfo import ZoneInfo
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from app.enums.status import MeetingStatus
from app.repositories.company_repository import CompanyRepository
from app.repositories.manager_repository import ManagerRepository
from app.repositories.meeting_repository import MeetingRepository
from app.schemas.meeting import MeetingCreate, MeetingRead, MeetingUpdate

ALMATY_TZ = ZoneInfo("Asia/Almaty")
MEETING_DURATION = timedelta(hours=1)
WORK_START = time(9, 0)
WORK_END = time(18, 0)

def validate_start(start_time: datetime) -> datetime:
  if start_time.tzinfo is None or start_time.utcoffset() is None:
    raise HTTPException(status_code=422, detail="start_time должно быть UTC (ISO 8601)")
  start = start_time.astimezone(timezone.utc)
  end = start + MEETING_DURATION
  start_local = start.astimezone(ALMATY_TZ)
  end_local = end.astimezone(ALMATY_TZ)
  fits_day = start_local.date() == end_local.date()
  weekday = start_local.weekday() < 5
  inside_hours = start_local.time() >= WORK_START and end_local.time() <= WORK_END
  if not (fits_day and weekday and inside_hours):
    raise HTTPException(status_code=422, detail="Встреча должна начинаться в будний день и полностью соответствовать месту 09:00-18:00 Азия/Алматы. Продолжительность - 60 минут, поэтому самое позднее начало - 17:00.")
  return start

class MeetingService:
  def __init__(self, session: AsyncSession):
    self.session = session
    self.repository = MeetingRepository(session)
    self.company_repository = CompanyRepository(session)
    self.manager_repository = ManagerRepository(session)

  async def create_meeting(self, payload: MeetingCreate):
    start = validate_start(payload.start_time)
    end = start + MEETING_DURATION
    company = await self.company_repository.get_for_update(payload.company_id)
    if not company:
      raise HTTPException(status_code=404, detail="Компания не найдена")
    manager = await self.manager_repository.get_for_update(payload.manager_id)
    if not manager:
      raise HTTPException(status_code=404, detail="Менеджер не найден")
    await self._ensure_free(manager_id=payload.manager_id, company_id=payload.company_id, start=start, end=end)
    try:
      meeting = await self.repository.insert(
        company_id=payload.company_id,
        manager_id=payload.manager_id,
        start_time=start,
        end_time=end,
        original_scheduled_at=start,
        status=MeetingStatus.scheduled,
      )
      await self.session.commit()
    except IntegrityError:
      await self.session.rollback()
      raise HTTPException(status_code=409, detail="Встреча пересекается с другой активной встречей")
    return MeetingRead.model_validate(meeting)

  async def update_meeting(self, meeting_id: int, payload: MeetingUpdate):
    if payload.start_time is None and payload.status is None:
      raise HTTPException(status_code=422, detail="Пройдите start_time для переноса или status cancelled для отмены")
    if payload.status is not None and payload.status != MeetingStatus.cancelled:
      raise HTTPException(status_code=422, detail="Отмена только через статус")
    if payload.start_time is not None and payload.status is not None:
      raise HTTPException(status_code=422, detail="Пройдите start_time для переноса или status cancelled для отмены")
    current = await self.repository.get_by_id(meeting_id)
    if not current:
      raise HTTPException(status_code=404, detail="Встреча не найдена")
    await self.company_repository.get_for_update(current.company_id)
    await self.manager_repository.get_for_update(current.manager_id)
    meeting = await self.repository.get_for_update(meeting_id)
    if meeting is None:
      raise HTTPException(status_code=404, detail="Встреча не найдна")
    if payload.status == MeetingStatus.cancelled:
      updated = await self.repository.update_fields(meeting.id, status=MeetingStatus.cancelled)
      await self.session.commit()
      return MeetingRead.model_validate(updated)
    if meeting.status == MeetingStatus.cancelled:
      raise HTTPException(status_code=409, detail="Отмененная встреча не может быть перенесена")
    start = validate_start(payload.start_time)
    end = start + MEETING_DURATION
    await self._ensure_free(manager_id=meeting.manager_id, company_id=meeting.company_id, start=start, end=end, exclude_id=meeting.id)
    try:
      updated = await self.repository.update_fields(meeting.id, start_time=start, end_time=end)
      await self.session.commit()
    except IntegrityError:
      await self.session.rollback()
      raise HTTPException(status_code=409, detail="Встреча пересекается с другой активной встречей")
    return MeetingRead.model_validate(updated)

  async def _ensure_free(self, manager_id: int, company_id: int, start: datetime, end: datetime, exclude_id: int | None = None):
    manager_overlap = await self.repository.find_overlapping(manager_id=manager_id, company_id=None, start_time=start, end_time=end, exclude_id=exclude_id)
    if manager_overlap:
      raise HTTPException(status_code=409, detail="Менеджер занят в это время")
    company_overlap = await self.repository.find_overlapping(manager_id=None, company_id=company_id, start_time=start, end_time=end, exclude_id=exclude_id)
    if company_overlap:
      raise HTTPException(status_code=409, detail="Компания занята в это время")
