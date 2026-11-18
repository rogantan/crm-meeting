from app.db.base import Base
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, String, Enum
from app.enums.status import CompanyStatus

class Company(Base):
  id: Mapped[int] = mapped_column(Integer, primary_key=True)
  name: Mapped[str] = mapped_column(String(255), nullable=False)
  bin: Mapped[str] = mapped_column(String(12), unique=True, nullable=False)
  status: Mapped[CompanyStatus] = mapped_column(Enum(CompanyStatus), default="new", nullable=False)