from app.db.base import Base
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, String, Enum, ForeignKey
from app.enums.result import CallResult

class Call(Base):
  id: Mapped[int] = mapped_column(Integer, primary_key=True)
  company_id: Mapped[int] = mapped_column(ForeignKey("company.id"), nullable=False)
  meeting_id: Mapped[int] = mapped_column(ForeignKey("meeting.id"), nullable=True)
  result: Mapped[CallResult] = mapped_column(Enum(CallResult), nullable=False)
