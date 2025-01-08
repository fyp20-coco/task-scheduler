import json
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from fastapi import HTTPException

user_creds = {
    'token': '{ "token_uri": "https://oauth2.googleapis.com/token", "client_id": "156269526706-r444o436o3nocmm02fpa19t5a9i9usrp.apps.googleusercontent.com", "client_secret": "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", "scopes": ["https://www.googleapis.com/auth/calendar"]}',
}


# def get_calendar_service():
#     print("this one runs")
#     if 'token' not in user_creds:
#         raise HTTPException(status_code=401, detail='User not authenticated')

#     creds = Credentials.from_authorized_user_info(json.loads(user_creds['token']))

#     if creds and creds.expired and creds.refresh_token:
#         creds.refresh(Request())

#     return build('calendar', 'v3', credentials=creds)
