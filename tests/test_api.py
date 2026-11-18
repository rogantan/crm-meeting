import psycopg2
import pytest
from tests.conftest import postgres_dsn

# Monday 2026-11-16. Asia/Almaty is UTC+5, so 10:00 local is 05:00 UTC.
MONDAY_0900 = "2026-11-16T04:00:00Z"
MONDAY_0859 = "2026-11-16T03:59:00Z"
MONDAY_10 = "2026-11-16T05:00:00Z"
MONDAY_1030 = "2026-11-16T05:30:00Z"
MONDAY_11 = "2026-11-16T06:00:00Z"
MONDAY_12 = "2026-11-16T07:00:00Z"
MONDAY_17 = "2026-11-16T12:00:00Z"
MONDAY_1730 = "2026-11-16T12:30:00Z"
TUESDAY_10 = "2026-11-17T05:00:00Z"
SATURDAY_10 = "2026-11-21T05:00:00Z"
# Friday 19:30 UTC is Saturday 00:30 in Almaty.
FRIDAY_EVENING_UTC = "2026-11-20T19:30:00Z"

COUNTER = {"n": 0}


def new_company(client, name="Company"):
  COUNTER["n"] += 1
  response = client.post("/companies", json={
    "name": name,
    "bin": f"{COUNTER['n']:012d}",
    "phone": "+77010000000",
  })
  assert response.status_code == 200, response.text
  return response.json()


def new_manager(client, name="Manager"):
  response = client.post("/managers", json={"name": name})
  assert response.status_code == 200, response.text
  return response.json()


def book(client, company_id, manager_id, start):
  return client.post("/meetings", json={
    "company_id": company_id,
    "manager_id": manager_id,
    "start_time": start,
  })


def test_manager_overlap_and_adjacent_slot(client):
  manager = new_manager(client)
  first = book(client, new_company(client)["id"], manager["id"], MONDAY_10)
  adjacent = book(client, new_company(client)["id"], manager["id"], MONDAY_11)
  overlap = book(client, new_company(client)["id"], manager["id"], MONDAY_1030)
  assert first.status_code == 200, first.text
  assert adjacent.status_code == 200, adjacent.text
  assert overlap.status_code == 409
  assert overlap.json()["detail"] == "Manager already has a meeting in this time slot"


def test_company_cannot_have_two_active_meetings(client):
  company = new_company(client)
  other = new_company(client)
  manager_a = new_manager(client, "A")
  manager_b = new_manager(client, "B")
  manager_c = new_manager(client, "C")
  assert book(client, company["id"], manager_a["id"], MONDAY_10).status_code == 200
  same_time = book(client, other["id"], manager_b["id"], MONDAY_10)
  assert same_time.status_code == 200, same_time.text
  conflict = book(client, company["id"], manager_c["id"], MONDAY_1030)
  assert conflict.status_code == 409
  assert conflict.json()["detail"] == "Company already has an active meeting in this time slot"


def test_working_day_boundary(client):
  manager = new_manager(client)
  company = new_company(client)
  opening = book(client, company["id"], manager["id"], MONDAY_0900)
  closing = book(client, new_company(client)["id"], manager["id"], MONDAY_17)
  too_early = book(client, new_company(client)["id"], manager["id"], MONDAY_0859)
  too_late = book(client, new_company(client)["id"], manager["id"], MONDAY_1730)
  naive = book(client, new_company(client)["id"], manager["id"], "2026-11-16T05:00:00")
  assert opening.status_code == 200, opening.text
  assert closing.status_code == 200, closing.text
  assert too_early.status_code == 422
  assert too_late.status_code == 422
  assert "17:00" in too_late.json()["detail"]
  assert naive.status_code == 422


def test_weekend_is_rejected(client):
  manager = new_manager(client)
  weekend = book(client, new_company(client)["id"], manager["id"], SATURDAY_10)
  utc_friday_but_almaty_saturday = book(client, new_company(client)["id"], manager["id"], FRIDAY_EVENING_UTC)
  assert weekend.status_code == 422
  assert utc_friday_but_almaty_saturday.status_code == 422


def test_reschedule_keeps_original_time_and_cancel_frees_slot(client):
  manager = new_manager(client)
  company = new_company(client)
  other = new_company(client)
  created = book(client, company["id"], manager["id"], MONDAY_10)
  assert created.status_code == 200, created.text
  meeting_id = created.json()["id"]
  moved = client.patch(f"/meetings/{meeting_id}", json={"start_time": MONDAY_12})
  assert moved.status_code == 200, moved.text
  assert moved.json()["original_scheduled_at"].startswith("2026-11-16T05:00:00")
  assert moved.json()["start_time"].startswith("2026-11-16T07:00:00")
  assert moved.json()["end_time"].startswith("2026-11-16T08:00:00")
  taken = book(client, other["id"], manager["id"], MONDAY_10)
  assert taken.status_code == 200, taken.text
  conflict = client.patch(f"/meetings/{meeting_id}", json={"start_time": MONDAY_10})
  assert conflict.status_code == 409
  cancelled = client.patch(f"/meetings/{taken.json()['id']}", json={"status": "cancelled"})
  assert cancelled.status_code == 200
  assert cancelled.json()["status"] == "cancelled"
  assert cancelled.json()["original_scheduled_at"].startswith("2026-11-16T05:00:00")
  again = book(client, other["id"], manager["id"], MONDAY_10)
  assert again.status_code == 200, again.text
  schedule = client.get(f"/managers/{manager['id']}/schedule", params={"date": "2026-11-16"})
  ids = [item["id"] for item in schedule.json()["meetings"]]
  assert taken.json()["id"] not in ids
  assert meeting_id in ids
  assert again.json()["id"] in ids


def test_schedule_returns_almaty_day(client):
  manager = new_manager(client)
  first = book(client, new_company(client)["id"], manager["id"], MONDAY_10)
  second = book(client, new_company(client)["id"], manager["id"], MONDAY_11)
  third = book(client, new_company(client)["id"], manager["id"], TUESDAY_10)
  assert first.status_code == 200 and second.status_code == 200 and third.status_code == 200
  response = client.get(f"/managers/{manager['id']}/schedule", params={"date": "2026-11-16"})
  assert response.status_code == 200
  body = response.json()
  assert body["date"] == "2026-11-16"
  assert len(body["meetings"]) == 2
  assert body["meetings"][0]["start_time"].startswith("2026-11-16T05:00:00")
  assert body["meetings"][1]["start_time"].startswith("2026-11-16T06:00:00")
  missing = client.get("/managers/999/schedule", params={"date": "2026-11-16"})
  assert missing.status_code == 404


def test_call_meeting_set_requires_meeting(client):
  company = new_company(client)
  other = new_company(client)
  manager = new_manager(client)
  missing = client.post("/calls", json={"company_id": company["id"], "result": "meeting_set"})
  assert missing.status_code == 422
  assert "created meeting" in missing.json()["detail"]
  created = book(client, company["id"], manager["id"], MONDAY_10)
  assert created.status_code == 200, created.text
  wrong_company = client.post("/calls", json={
    "company_id": other["id"],
    "result": "meeting_set",
    "meeting_id": created.json()["id"],
  })
  assert wrong_company.status_code == 422
  linked = client.post("/calls", json={
    "company_id": company["id"],
    "result": "meeting_set",
    "meeting_id": created.json()["id"],
  })
  assert linked.status_code == 200, linked.text
  assert linked.json()["meeting_id"] == created.json()["id"]
  listed = client.get("/companies", params={"status": "meeting_set"})
  assert [item["id"] for item in listed.json()["items"]] == [company["id"]]
  refused = client.post("/calls", json={"company_id": other["id"], "result": "refused", "meeting_id": created.json()["id"]})
  assert refused.status_code == 422


def test_companies_pagination_and_call_status(client):
  first = new_company(client, "One")
  second = new_company(client, "Two")
  third = new_company(client, "Three")
  page = client.get("/companies", params={"page": 1, "size": 2})
  assert page.status_code == 200
  body = page.json()
  assert body["total"] == 3
  assert len(body["items"]) == 2
  assert body["items"][0]["phone"] == "+77010000000"
  call = client.post("/calls", json={"company_id": first["id"], "result": "no_answer"})
  assert call.status_code == 200, call.text
  called = client.get("/companies", params={"status": "called"})
  assert [item["id"] for item in called.json()["items"]] == [first["id"]]
  fresh_ids = [item["id"] for item in client.get("/companies", params={"status": "new"}).json()["items"]]
  assert first["id"] not in fresh_ids
  assert second["id"] in fresh_ids and third["id"] in fresh_ids
  duplicate = client.post("/companies", json={"name": "Dup", "bin": first["bin"], "phone": "12345"})
  assert duplicate.status_code == 409
  assert client.get("/companies", params={"status": "nope"}).status_code == 422


def test_database_exclusion_constraint(client):
  manager = new_manager(client)
  company_a = new_company(client)
  company_b = new_company(client)
  first = book(client, company_a["id"], manager["id"], MONDAY_10)
  assert first.status_code == 200, first.text
  conn = psycopg2.connect(postgres_dsn())
  conn.autocommit = True
  cur = conn.cursor()
  with pytest.raises(psycopg2.Error) as exc:
    cur.execute(
      """
      INSERT INTO meeting (company_id, manager_id, start_time, end_time, original_scheduled_at, status)
      VALUES (%s, %s, %s, %s, %s, 'scheduled')
      """,
      (company_b["id"], manager["id"], "2026-11-16T05:30:00+00", "2026-11-16T06:30:00+00", "2026-11-16T05:30:00+00"),
    )
  cur.close()
  conn.close()
  constraint = getattr(getattr(exc.value, "diag", None), "constraint_name", "")
  assert constraint == "meeting_manager_no_overlap" or "meeting_manager_no_overlap" in str(exc.value)
