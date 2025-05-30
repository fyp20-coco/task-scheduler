from fastapi import APIRouter, HTTPException,Query
from app.services.calendar_service import create_event, delete_event, get_event,get_event_timeframe
from datetime import datetime

router = APIRouter()

@router.post("/create/manual")
def create_event_endpoint(payload: dict):
    """
    Creates a Google Calendar event.
    """
    start_time = payload.get("StartTime")
    end_time = payload.get("EndTime")
    title = payload.get("Subject")
    location = payload.get("Location")
    description = payload.get("Description")
    recurrence_rule = payload.get("RecurrenceRule")
    print("start_time",start_time)
    print("end_time",end_time)
    print("title",title)
    print("location",location)
    print("description",description)
    print("recurrence_rule",recurrence_rule)

    
    return "Event created successfully"
@router.post("/create")
def create_event_endpoint(start_time: datetime, end_time: datetime, description: str, title: str):
    """
    Creates a Google Calendar event.
    """
    event_id = create_event(start_time, end_time, description, title)
    if not event_id:
        raise HTTPException(status_code=500, detail="Failed to create event.")
    return {"event_id": event_id}


@router.get("/events")
def get_events(limit: int = 10):
    """
    Fetches a list of upcoming events.
    """
    return get_event(limit)
# @router.get("/events")
# def get_events_from_db(limit: int = 10):
#     """
#     Fetches a list of upcoming events.
#     """
#     return get_event(limit)

@router.get("/events/timeframe")
def get_events_timeframe(start: datetime = Query(..., alias="startDate"),
    end: datetime = Query(..., alias="endDate")):
    """
    Fetches a list of upcoming events.
    """
    return get_event_timeframe(start,end)


@router.delete("/delete/{event_id}")
def delete_event_endpoint(event_id: str):
    """
    Deletes a Google Calendar event by event ID.
    """
    delete_event(event_id)
    return {"message": f"Event {event_id} deleted successfully."}


