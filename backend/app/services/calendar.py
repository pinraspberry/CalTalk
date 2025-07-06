from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from datetime import datetime, timedelta
import os.path
import pickle
from typing import List, Optional, Dict, Any
from ..config import get_settings

SCOPES = ['https://www.googleapis.com/auth/calendar']

class CalendarService:
    def __init__(self):
        self.settings = get_settings()
        self.creds = None
        self.service = None
        self._authenticate()

    def _authenticate(self):
        """Handle Google Calendar authentication."""
        # Check if we have valid credentials
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                self.creds = pickle.load(token)

        # If there are no (valid) credentials available, let the user log in
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                # Check if we have client credentials
                if not self.settings.GOOGLE_CLIENT_ID or not self.settings.GOOGLE_CLIENT_SECRET:
                    raise Exception("Google Calendar credentials not configured. Please set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET in your .env file.")
                
                flow = InstalledAppFlow.from_client_config(
                    {
                        "installed": {
                            "client_id": self.settings.GOOGLE_CLIENT_ID,
                            "client_secret": self.settings.GOOGLE_CLIENT_SECRET,
                            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                            "token_uri": "https://oauth2.googleapis.com/token",
                            "redirect_uris": ["http://localhost:8080"]
                        }
                    },
                    SCOPES
                )
                self.creds = flow.run_local_server(port=8080)

            # Save the credentials for the next run
            with open('token.pickle', 'wb') as token:
                pickle.dump(self.creds, token)

        self.service = build('calendar', 'v3', credentials=self.creds)

    def create_event(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new calendar event in Google Calendar."""
        # Ensure we have required fields
        if not event_data.get('title'):
            event_data['title'] = "Untitled Event"
        
        if not event_data.get('start_time'):
            event_data['start_time'] = datetime.now()
            
        if not event_data.get('end_time'):
            event_data['end_time'] = event_data['start_time'] + timedelta(minutes=60)

        event = {
            'summary': event_data['title'],
            'start': {
                'dateTime': event_data['start_time'].isoformat(),
                'timeZone': self.settings.DEFAULT_TIMEZONE,
            },
            'end': {
                'dateTime': event_data['end_time'].isoformat(),
                'timeZone': self.settings.DEFAULT_TIMEZONE,
            },
            'description': event_data.get('description', ''),
            'location': event_data.get('location', ''),
            'attendees': [{'email': email} for email in (event_data.get('attendees') or [])],
            'reminders': {
                'useDefault': False,
                'overrides': [
                    {'method': 'email', 'minutes': self.settings.DEFAULT_REMINDER_MINUTES},
                    {'method': 'popup', 'minutes': self.settings.DEFAULT_REMINDER_MINUTES},
                ],
            },
        }

        created_event = self.service.events().insert(calendarId='primary', body=event).execute()
        return created_event

    def get_daily_agenda(self, date: datetime) -> List[Dict[str, Any]]:
        """Get all events for a specific day from Google Calendar."""
        start_time = date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_time = start_time + timedelta(days=1)

        events_result = self.service.events().list(
            calendarId='primary',
            timeMin=start_time.isoformat() + 'Z',
            timeMax=end_time.isoformat() + 'Z',
            singleEvents=True,
            orderBy='startTime'
        ).execute()

        return events_result.get('items', [])

    def check_conflicts(self, start_time: datetime, end_time: datetime) -> List[Dict[str, Any]]:
        """Check for conflicting events in the given time range."""
        events_result = self.service.events().list(
            calendarId='primary',
            timeMin=start_time.isoformat() + 'Z',
            timeMax=end_time.isoformat() + 'Z',
            singleEvents=True,
            orderBy='startTime'
        ).execute()

        return events_result.get('items', [])

    def update_event(self, event_id: str, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing calendar event."""
        event = self.service.events().get(calendarId='primary', eventId=event_id).execute()
        
        # Update event fields
        event.update({
            'summary': event_data.get('title', event['summary']),
            'start': {
                'dateTime': event_data.get('start_time', event['start']['dateTime']),
                'timeZone': self.settings.DEFAULT_TIMEZONE,
            },
            'end': {
                'dateTime': event_data.get('end_time', event['end']['dateTime']),
                'timeZone': self.settings.DEFAULT_TIMEZONE,
            },
        })

        updated_event = self.service.events().update(
            calendarId='primary',
            eventId=event_id,
            body=event
        ).execute()

        return updated_event

    def delete_event(self, event_id: str) -> None:
        """Delete a calendar event from Google Calendar."""
        self.service.events().delete(calendarId='primary', eventId=event_id).execute()

    def find_free_slots(self, date: datetime, duration_minutes: int) -> List[Dict[str, datetime]]:
        """Find free time slots for a given duration on a specific date."""
        start_time = date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_time = start_time + timedelta(days=1)
        
        # Get all events for the day
        events = self.get_daily_agenda(date)
        
        # Convert events to time slots
        busy_slots = []
        for event in events:
            start = datetime.fromisoformat(event['start']['dateTime'].replace('Z', '+00:00'))
            end = datetime.fromisoformat(event['end']['dateTime'].replace('Z', '+00:00'))
            busy_slots.append((start, end))
        
        # Find free slots
        free_slots = []
        current_time = start_time
        
        while current_time < end_time:
            slot_end = current_time + timedelta(minutes=duration_minutes)
            if slot_end > end_time:
                break
                
            is_free = True
            for busy_start, busy_end in busy_slots:
                if (current_time < busy_end and slot_end > busy_start):
                    is_free = False
                    current_time = busy_end
                    break
            
            if is_free:
                free_slots.append({
                    'start': current_time,
                    'end': slot_end
                })
                current_time = slot_end
            else:
                current_time += timedelta(minutes=15)
        
        return free_slots 