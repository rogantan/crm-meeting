from fastapi import APIRouter, Depends
from app.api.dependencies import get_meeting_service
from app.schemas.meeting import MeetingCreate, MeetingUpdate
from app.services.meeting_service import MeetingService

router = APIRouter(prefix="/meetings", tags=["Meetings"])

@router.post("")
async def create_meeting(data: MeetingCreate, meeting_service: MeetingService = Depends(get_meeting_service)):
  return await meeting_service.create_meeting(data)

@router.patch("/{meeting_id}")
async def update_meeting(meeting_id: int, data: MeetingUpdate, meeting_service: MeetingService = Depends(get_meeting_service)):
  return await meeting_service.update_meeting(meeting_id, data)
