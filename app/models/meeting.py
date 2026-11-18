from app.db.base import Base
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, String, Enum, ForeignKey, DateTime
from datetime import datetime
from app.enums.status import MeetingStatus

class Meeting(Base):
  id: Mapped[int] = mapped_column(Integer, primary_key=True)
  company_id: Mapped[int] = mapped_column(ForeignKey("company.id"), nullable=False)
  manager_id: Mapped[int] = mapped_column(ForeignKey("manager.id"), nullable=False)
  start_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
  end_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
  original_scheduled_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
  status: Mapped[MeetingStatus] = mapped_column(Enum(MeetingStatus), default="scheduled", nullable=False)