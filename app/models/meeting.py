from datetime import datetime
from sqlalchemy import CheckConstraint, DateTime, Enum, ForeignKey, Integer, literal_column
from sqlalchemy.dialects.postgresql import ExcludeConstraint
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base
from app.enums.status import MeetingStatus

class Meeting(Base):
  __table_args__ = (
    CheckConstraint(
      "end_time = start_time + interval '1 hour'",
      name="meeting_duration_60min",
    ),
  )
  id: Mapped[int] = mapped_column(Integer, primary_key=True)
  company_id: Mapped[int] = mapped_column(ForeignKey("company.id"), nullable=False)
  manager_id: Mapped[int] = mapped_column(ForeignKey("manager.id"), nullable=False)
  start_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
  end_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
  original_scheduled_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
  status: Mapped[MeetingStatus] = mapped_column(Enum(MeetingStatus), default="scheduled", nullable=False)

Meeting.__table__.append_constraint(ExcludeConstraint(
  (Meeting.__table__.c.manager_id, "="),
  (literal_column("tstzrange(start_time, end_time, '[)')"), "&&"),
  where="status = 'scheduled'::meetingstatus",
  using="gist",
  name="meeting_manager_no_overlap",
))
Meeting.__table__.append_constraint(ExcludeConstraint(
  (Meeting.__table__.c.company_id, "="),
  (literal_column("tstzrange(start_time, end_time, '[)')"), "&&"),
  where="status = 'scheduled'::meetingstatus",
  using="gist",
  name="meeting_company_no_overlap",
))