from enum import Enum

class CompanyStatus(Enum):
  new = "new"
  called = "called"
  refused = "refused"
  meeting_set = "meeting_set"

class MeetingStatus(Enum):
  scheduled = "scheduled"
  cancelled = "cancelled"