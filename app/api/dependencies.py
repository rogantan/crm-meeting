from app.services.call_service import CallService
from app.services.company_service import CompanyService
from app.services.manager_service import ManagerService
from app.services.meeting_service import MeetingService
from fastapi import Depends
from app.db.db_postgres import get_session
from sqlalchemy.ext.asyncio import AsyncSession


def get_company_service(session: AsyncSession = Depends(get_session)):
  return CompanyService(session)

def get_call_service(session: AsyncSession = Depends(get_session)):
  return CallService(session)

def get_meeting_service(session: AsyncSession = Depends(get_session)):
  return MeetingService(session)

def get_manager_service(session: AsyncSession = Depends(get_session)):
  return ManagerService(session)