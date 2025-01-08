from datetime import datetime
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError




# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/calendar.events","https://www.googleapis.com/auth/calendar"]

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import os

def get_service():
    # SCOPES = ["https://www.googleapis.com/auth/calendar"]
    creds = None

    # Check for token.json file to use existing credentials
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)

    # If no valid credentials are available, prompt the user to log in
    if not creds or not creds.valid:
        from google.auth.transport.requests import Request
        from google_auth_oauthlib.flow import InstalledAppFlow

        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)

        # Save the credentials for the next run
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    # Build the service object
    service = build("calendar", "v3", credentials=creds)
    return service



def get_event(limit):
  """Shows basic usage of the Google Calendar API.
  Prints the start and name of the next 10 events on the user's calendar.
  """
  creds = None
  # The file token.json stores the user's access and refresh tokens, and is
  # created automatically when the authorization flow completes for the first
  # time.
  if os.path.exists("token.json"):
    creds = Credentials.from_authorized_user_file("token.json", SCOPES)
  # If there are no (valid) credentials available, let the user log in.
  if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
      creds.refresh(Request())
    else:
      flow = InstalledAppFlow.from_client_secrets_file(
          "credentials.json", SCOPES
      )
      creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open("token.json", "w") as token:
      token.write(creds.to_json())

  try:
    service = build("calendar", "v3", credentials=creds)

    # Call the Calendar API
    now = datetime.datetime.utcnow().isoformat() + "Z"  # 'Z' indicates UTC time
    print("Getting the upcoming 10 events")
    events_result = (
        service.events()
        .list(
            calendarId="primary",
            timeMin=now,
            maxResults=limit,
            singleEvents=True,
            orderBy="startTime",
        )
        .execute()
    )
    events = events_result.get("items", [])

    if not events:
      print("No upcoming events found.")
      return

    # Prints the start and name of the next 10 events
    for event in events:
      start = event["start"].get("dateTime", event["start"].get("date"))
      print(start, event["summary"])

  except HttpError as error:
    print(f"An error occurred: {error}")

def delete_event(event_id):
  # SCOPES = ["https://www.googleapis.com/auth/calendar.events"]
  """Shows basic usage of the Google Calendar API.
  Prints the start and name of the next 10 events on the user's calendar.
  """
  creds = None
  # The file token.json stores the user's access and refresh tokens, and is
  # created automatically when the authorization flow completes for the first
  # time.
  if os.path.exists("token.json"):
    creds = Credentials.from_authorized_user_file("token.json", SCOPES)
  # If there are no (valid) credentials available, let the user log in.
  if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
      creds.refresh(Request())
    else:
      flow = InstalledAppFlow.from_client_secrets_file(
          "credentials.json", SCOPES
      )
      creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open("token.json", "w") as token:
      token.write(creds.to_json())

  try:
    service = build("calendar", "v3", credentials=creds)

    # Call the Calendar API
    service.events().delete(calendarId='primary', eventId=event_id).execute()

    print(f"Event deleted: {event_id}")

  except HttpError as error:
    print(f"An error occurred: {error}")




# def create_event(event):
#   """Shows basic usage of the Google Calendar API.
#   Prints the start and name of the next 10 events on the user's calendar.
#   """
#   creds = None
#   # The file token.json stores the user's access and refresh tokens, and is
#   # created automatically when the authorization flow completes for the first
#   # time.
#   if os.path.exists("token.json"):
#     creds = Credentials.from_authorized_user_file("token.json", SCOPES)
#   # If there are no (valid) credentials available, let the user log in.
#   if not creds or not creds.valid:
#     if creds and creds.expired and creds.refresh_token:
#       creds.refresh(Request())
#     else:
#       flow = InstalledAppFlow.from_client_secrets_file(
#           "credentials.json", SCOPES
#       )
#       creds = flow.run_local_server(port=0)
#     # Save the credentials for the next run
#     with open("token.json", "w") as token:
#       token.write(creds.to_json())

#   try:
#     service = build("calendar", "v3", credentials=creds)

#     event = service.events().insert(calendarId='primary', body=event).execute()

#     print(f"Event created: {event.get('id')}")

#   except HttpError as error:
#     print(f"An error occurred: {error}")


def create_event(start_time, end_time, description, summary, calendar_id="primary"):
    """
    Creates a Google Calendar event.
    """
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
    import os

    SCOPES = ["https://www.googleapis.com/auth/calendar"]
    creds = None

    # Check for token.json
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)

    # If token.json is missing or invalid, prompt the user to log in
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("app/services/credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)

        # Save the credentials for future use
        with open("token.json", "w") as token_file:
            token_file.write(creds.to_json())

    # Initialize the Google Calendar service
    service = build("calendar", "v3", credentials=creds)

    # Ensure start_time and end_time are ISO 8601 strings
    if isinstance(start_time, datetime):
        start_time = start_time.isoformat()
    if isinstance(end_time, datetime):
        end_time = end_time.isoformat()

    event_data = {
        "summary": summary,
        "description": description,
        "start": {"dateTime": start_time, "timeZone": "Asia/Colombo"},
        "end": {"dateTime": end_time, "timeZone": "Asia/Colombo"},
    }

    try:
        event = service.events().insert(calendarId=calendar_id, body=event_data).execute()
        print(f"Event created: {event.get('id')}")
        return event.get("id")
    except Exception as e:
        print(f"An error occurred: {e}")
        return None


def main():
  
  get_event(10)
  # create_event({
  #   'summary': 'Google I/O 2022',
  #   'location': '800 Howard St., San Francisco, CA 94103',
  #   'description': 'A chance to hear more about Google\'s developer products.',
  #   'start': {
  #     'dateTime': '2024-12-11T09:00:00',
  #     'timeZone': 'Asia/Colombo',
  #   },
  #   'end': {
  #     'dateTime': '2024-12-11T17:02:00',
  #     'timeZone': 'Asia/Colombo',
  #   },
  #   'recurrence': [
  #     'RRULE:FREQ=DAILY;COUNT=1'
  #   ],
  # })  
  

  # service = get_service()
  
  # calendar_list = service.calendarList().list().execute()
  # # for calendar in calendar_list.get("items", []):
  # #     print(f"Calendar ID: {calendar['id']} - Summary: {calendar['summary']}")  
  # events_result = service.events().list(calendarId="primary").execute()
  # for event in events_result.get("items", []):
  #   print(f"Event ID: {event['id']} - Summary: {event.get('summary', 'N/A')}")



if __name__ == "__main__":
  main()