import datetime
import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Права доступа к календарю
SCOPES = ['https://www.googleapis.com/auth/calendar.events']

def create_calendar_event(task):
    creds = None

    # Авторизация пользователя через OAuth
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    service = build('calendar', 'v3', credentials=creds)

    # Формируем событие
    event = {
        'summary': task.title,
        'description': task.description,
        'start': {
            'dateTime': task.deadline.isoformat(),
            'timeZone': 'Asia/Almaty',
        },
        'end': {
            'dateTime': (task.deadline + datetime.timedelta(hours=1)).isoformat(),
            'timeZone': 'Asia/Almaty',
        },
    }

    # Отправляем событие в календарь
    service.events().insert(calendarId='primary', body=event).execute()
