from sqlalchemy import select, update
from app.enums.status import MeetingStatus
from app.models.meeting import Meeting
from app.repositories.abstract_repository import AbstractRepository

class MeetingRepository(AbstractRepository):
  def __init__(self, session):
    super().__init__(model=Meeting, session=session)

  async def find_overlapping(self, manager_id: int | None, company_id: int | None, start_time, end_time, exclude_id: int | None = None):
    query = select(Meeting).where(
      Meeting.status == MeetingStatus.scheduled,
      Meeting.start_time < end_time,
      Meeting.end_time > start_time,
    )
    if manager_id is not None:
      query = query.where(Meeting.manager_id == manager_id)
    if company_id is not None:
      query = query.where(Meeting.company_id == company_id)
    if exclude_id is not None:
      query = query.where(Meeting.id != exclude_id)
    result = await self.session.execute(query)
    return result.scalars().all()

  async def list_for_manager(self, manager_id: int, range_start, range_end):
    query = select(Meeting).where(
      Meeting.manager_id == manager_id,
      Meeting.status == MeetingStatus.scheduled,
      Meeting.start_time < range_end,
      Meeting.end_time > range_start,
    ).order_by(Meeting.start_time)
    result = await self.session.execute(query)
    return result.scalars().all()

  async def update_fields(self, meeting_id: int, **data):
    query = update(Meeting).where(Meeting.id == meeting_id).values(**data)
    result = await self.session.execute(query.returning(Meeting))
    return result.scalars().one()
