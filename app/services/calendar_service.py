from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from datetime import datetime
import os

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
    event_data = {
        "title": title,
        "description": description,
        "start": {"dateTime": start_time, "timeZone": "Asia/Colombo"},
        "end": {"dateTime": end_time, "timeZone": "Asia/Colombo"},
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
