from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from datetime import datetime, timedelta
import os
from sqlalchemy.orm import Session

SCOPES = ["https://www.googleapis.com/auth/calendar.events","https://www.googleapis.com/auth/calendar"]

def get_service():
    """
    Initializes and returns the Google Calendar API service with valid credentials.
    """
    creds = None
    if os.path.exists("token.json"):
        # Load credentials from the token.json file.
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    
    # Refresh or request new credentials if necessary.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            creds_path = os.path.join(os.path.dirname(__file__), "credentials.json")
            flow = InstalledAppFlow.from_client_secrets_file(
                creds_path, SCOPES
            )
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run.
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    # Build the Google Calendar API service.
    return build("calendar", "v3", credentials=creds)


def create_event(start_time, end_time, description, title, calendar_id="primary"):
    service = get_service()
    # Ensure start_time and end_time are in ISO format
    start_time_str = start_time.isoformat() if isinstance(start_time, datetime) else start_time
    end_time_str = end_time.isoformat() if isinstance(end_time, datetime) else end_time

    event_data = {
        "summary": title,  # Using 'summary' instead of 'title' to match Google Calendar API
        "description": description,
        "start": {"dateTime": start_time_str, "timeZone": "Asia/Colombo"},
        "end": {"dateTime": end_time_str, "timeZone": "Asia/Colombo"},
    }
    event = service.events().insert(calendarId=calendar_id, body=event_data).execute()
    return event.get("id")


def delete_event(event_id, calendar_id="primary"):
    service = get_service()
    service.events().delete(calendarId=calendar_id, eventId=event_id).execute()


def get_event(limit, calendar_id="primary"):
    """
    Fetches the next 'limit' number of events from the specified Google Calendar.

    Args:
        limit (int): The maximum number of events to fetch.
        calendar_id (str): The ID of the calendar to query. Defaults to 'primary'.

    Returns:
        list: A list of events from the calendar.
    """
    try:
        service = get_service()
        now = datetime.utcnow().isoformat() + "Z"  # UTC time in ISO 8601 format
        print("now",now)
        events_result = service.events().list(
            calendarId=calendar_id,
            timeMin=now,
            maxResults=limit,
            singleEvents=True,
            orderBy="startTime",
        ).execute()
        return events_result.get("items", [])
    except Exception as e:
        print(f"An error occurred: {e}")
        return []
    
def get_event_timeframe(start, end, calendar_id="primary"):
    """
    Fetches the next 'limit' number of events from the specified Google Calendar.

    Args:
        limit (int): The maximum number of events to fetch.
        calendar_id (str): The ID of the calendar to query. Defaults to 'primary'.

    Returns:
        list: A list of events from the calendar.
    """
    try:
        service = get_service()
        now = datetime.utcnow().isoformat() + "Z"  # UTC time in ISO 8601 format
        print("start",start)
        print("end",end)
        events_result = service.events().list(
            calendarId=calendar_id,
            timeMin=start.isoformat(),
            timeMax=end.isoformat(),
            singleEvents=True,
            orderBy="startTime",
        ).execute()

        eventlist=events_result.get("items", [])
        formatted_events = []
        # print("Event List:", eventlist)
        for event in eventlist:
            print(event['id'])
            print(event['start']['dateTime'])
            print(event['end']['dateTime'])
            print(event['description'])
            if 'summary' in event:
                print(event['summary'])
            # print(event['summary'])

        for index, event in enumerate(eventlist):
            # Extract date information safely
            start_time = event.get('start', {}).get('dateTime', '')
            end_time = event.get('end', {}).get('dateTime', '')
            
            # Build formatted event object
            formatted_event = {
                "Id": event.get('id', str(index + 1)),  # Use Google Calendar ID or fallback to index
                "Subject": event.get('summary', 'Untitled Event'),
                "StartTime": start_time,  # Keep as ISO string for frontend processing
                "EndTime": end_time,      # Keep as ISO string for frontend processing
                "Priority": "Medium",     # Default priority since not in Google Calendar
                "Status": "Scheduled",    # Default status
                "IsAllDay": False,        # Default to false
                "Location": event.get('location', ''),
                "Description": event.get('description', '')
            }
            formatted_events.append(formatted_event)    
        print("Formatted Event:", formatted_events)

        return formatted_events
    except Exception as e:
        print(f"An error occurred: {e}")
        return []  
def add_task_to_calendar(tasks, calendar_id="primary"):
    if not tasks:
        return []
    
    # Check if tasks is a single task rather than a list
    if not isinstance(tasks, list):
        tasks = [tasks]
    
    event_ids = []
    
    for task in tasks:
        # Handle both dictionary format and Task object format
        # if isinstance(task, dict):
        start_time = task.get("StartTime")
        end_time = task.get("EndTime")
        print("start_time",start_time)
        print("end_time",end_time)
        
        # If end_time is not provided, default to 1 hour after start_time
        if end_time is None and start_time is not None:
            end_time = start_time + timedelta(hours=1)
            
        description = task.get("Description", "")
        if "Priority" in task:
            description += f"\nPriority: {task.get('Priority')}"
        if "Status" in task:
            description += f"\nStatus: {task.get('Status')}"
        if "Location" in task:
            description += f"\nLocation: {task.get('Location')}"
            
        title = task.get("Subject", "Task")
        print(f"Creating event for task: {title} ,dsfss {description},{start_time}, {end_time},")
        # else:
            
        #     # Original behavior for Task objects
        #     start_time = task.deadline
        #     end_time = start_time + timedelta(hours=1)
        #     description = f"Task: {task.type}, Priority: {task.priority}, Chunks: {len(task.chunks)}"
        #     title = f"Task - {task.type}"
        
        # Create the event and store the ID
        event_id = create_event(start_time, end_time, description, title, calendar_id)
        print(f"Event created with ID: {event_id}")
        if event_id:
            event_ids.append(event_id)
    
    return event_ids

# def get_events_from_db(db: Session, limit: int):
#     """
#     Fetches the next 'limit' number of events from the database using SQLAlchemy.

#     Args:
#         db (Session): The SQLAlchemy session to use.
#         limit (int): The maximum number of events to fetch.

#     Returns:
#         list: A list of event dictionaries, formatted similarly to Google Calendar API.
#     """
#     try:
#         now = datetime.utcnow()
#         events_query = (
#             db.query(Event)
#             .filter(Event.start_time >= now)
#             .order_by(Event.start_time)
#             .limit(limit)
#             .all()
#         )

#         events = [
#             {
#                 "id": event.id,
#                 "summary": event.title,
#                 "description": event.description,
#                 "start": {"dateTime": event.start_time.isoformat(), "timeZone": "UTC"},
#                 "end": {"dateTime": event.end_time.isoformat(), "timeZone": "UTC"},
#             }
#             for event in events_query
#         ]

#         return events

#     except Exception as e:
#         print(f"Database error: {e}")
#         return []     
