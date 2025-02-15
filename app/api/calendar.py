from fastapi import APIRouter, HTTPException
from app.services.calendar_service import create_event, delete_event, get_event

router = APIRouter()

@router.post("/create")
def create_event_endpoint(start_time: str, end_time: str, description: str, title: str):
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


@router.delete("/delete/{event_id}")
def delete_event_endpoint(event_id: str):
    """
    Deletes a Google Calendar event by event ID.
    """
    delete_event(event_id)
    return {"message": f"Event {event_id} deleted successfully."}


