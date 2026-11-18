from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.enums.result import CallResult
from app.enums.status import CompanyStatus, MeetingStatus
from app.repositories.call_repository import CallRepository
from app.repositories.company_repository import CompanyRepository
from app.repositories.meeting_repository import MeetingRepository
from app.schemas.call import CallCreate, CallRead

class CallService:
  def __init__(self, session: AsyncSession):
    self.session = session
    self.repository = CallRepository(session)
    self.company_repository = CompanyRepository(session)
    self.meeting_repository = MeetingRepository(session)

  async def create_call(self, payload: CallCreate):
    company = await self.company_repository.get_for_update(payload.company_id)
    if not company:
      raise HTTPException(status_code=404, detail="Компания не найдена")
    if payload.result == CallResult.meeting_set:
      if payload.meeting_id is None:
        raise HTTPException(status_code=422, detail="Звонок с результатом meeting_set должен содержать встречу на эту компанию")
      meeting = await self.meeting_repository.get_for_update(payload.meeting_id)
      if meeting is None or meeting.company_id != payload.company_id or meeting.status != MeetingStatus.scheduled:
        raise HTTPException(status_code=422, detail="Звонок с результатом meeting_set должен содержать встречу на эту компанию")
    elif payload.meeting_id is not None:
      raise HTTPException(status_code=422, detail="meeting_id нужен, если результат звонка - meeting_set")
    call = await self.repository.insert(**payload.model_dump())
    if payload.result == CallResult.no_answer:
      company.status = CompanyStatus.called
    elif payload.result == CallResult.refused:
      company.status = CompanyStatus.refused
    else:
      company.status = CompanyStatus.meeting_set
    await self.session.commit()
    return CallRead.model_validate(call)
