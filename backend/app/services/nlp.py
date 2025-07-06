import google.generativeai as genai
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime, timedelta
import re
import json
from ..config import get_settings

class EventIntent(BaseModel):
    """Schema for parsed event intent from natural language."""
    action: str = Field(description="The action to perform (create, update, delete, query)")
    title: Optional[str] = Field(default=None, description="The title of the event")
    start_time: Optional[datetime] = Field(default=None, description="The start time of the event")
    end_time: Optional[datetime] = Field(default=None, description="The end time of the event")
    description: Optional[str] = Field(default=None, description="The description of the event")
    location: Optional[str] = Field(default=None, description="The location of the event")
    attendees: Optional[List[str]] = Field(default=None, description="List of attendees' email addresses")
    priority: Optional[str] = Field(default="medium", description="Priority level of the event")
    duration_minutes: Optional[int] = Field(default=60, description="Duration of the event in minutes")

class NLPService:
    def __init__(self):
        self.settings = get_settings()
        genai.configure(api_key=self.settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel(self.settings.MODEL_NAME)
        self.model.temperature = self.settings.TEMPERATURE

    def _create_prompt_template(self, user_input: str) -> str:
        """Create the prompt template for event parsing."""
        current_time = datetime.now()
        
        prompt = f"""You are a calendar assistant that helps parse natural language into structured event data.
        
Extract the following information from the user's input and return it as a JSON object:
- action: The action to perform (create, update, delete, query)
- title: The title of the event
- start_time: The start time of the event (ISO format)
- end_time: The end time of the event (ISO format)
- description: The description of the event
- location: The location of the event
- attendees: List of attendees' email addresses
- priority: Priority level of the event (low, medium, high, urgent)
- duration_minutes: Duration of the event in minutes

User input: {user_input}

Current time: {current_time.isoformat()}

Remember to:
1. Convert relative time references (e.g., "tomorrow", "next week") to actual dates
2. Extract email addresses for attendees
3. Determine the appropriate action based on the user's intent
4. Set default duration to 60 minutes if not specified
5. Set default priority to "medium" if not specified
6. Return only valid JSON format

Make sure that relative time phrases like "today", "tomorrow", "next week" are fully converted into ISO 8601 formatted timestamps, and NOT left as words.
Do NOT include date keywords like "today" or "tomorrow" in the event title.

Return the response as a JSON object with the extracted information."""
        
        return prompt

    def parse_event_intent(self, user_input: str) -> EventIntent:
        """Parse natural language input into structured event data."""
        prompt = self._create_prompt_template(user_input)
        
        # Get response from Gemini
        try:
            response = self.model.generate_content(prompt)
            response_text = response.text
            
            # Parse the response into EventIntent
            try:
                # Try to parse as JSON first
                if response_text.strip().startswith('{'):
                    json_data = json.loads(response_text)
                    return EventIntent(**json_data)
                else:
                    # Fallback to basic parsing if structured parsing fails
                    return self._fallback_parsing(user_input)
            except Exception as e:
                # Fallback to basic parsing if structured parsing fails
                return self._fallback_parsing(user_input)
        except Exception as e:
            # Fallback to basic parsing if API call fails
            return self._fallback_parsing(user_input)

    def _fallback_parsing(self, user_input: str) -> EventIntent:
        """Fallback method for basic event parsing when structured parsing fails."""
        # Basic regex patterns for common time expressions
        time_patterns = {
            r'tomorrow at (\d{1,2}(?::\d{2})? ?(?:AM|PM|am|pm)?)': lambda m: self._parse_time_tomorrow(m.group(1)),
            r'next (\w+) at (\d{1,2}(?::\d{2})? ?(?:AM|PM|am|pm)?)': lambda m: self._parse_time_next_weekday(m.group(1), m.group(2)),
            r'(\d{1,2}(?::\d{2})? ?(?:AM|PM|am|pm)?)': lambda m: self._parse_time_today(m.group(1))
        }

        # Extract time
        start_time = None
        for pattern, parser in time_patterns.items():
            match = re.search(pattern, user_input, re.IGNORECASE)
            if match:
                start_time = parser(match)
                break

        # Default duration if not specified
        duration_minutes = self.settings.DEFAULT_EVENT_DURATION

        # Create basic event intent
        return EventIntent(
            action="create",
            title=user_input.split(" at ")[0].strip(),
            start_time=start_time,
            end_time=start_time + timedelta(minutes=duration_minutes) if start_time else None,
            priority="medium"
        )

    def _parse_time_tomorrow(self, time_str: str) -> datetime:
        """Parse time string for tomorrow."""
        return self._parse_time(time_str, days_ahead=1)

    def _parse_time_next_weekday(self, weekday: str, time_str: str) -> datetime:
        """Parse time string for next weekday."""
        weekdays = {
            'monday': 0, 'tuesday': 1, 'wednesday': 2, 'thursday': 3,
            'friday': 4, 'saturday': 5, 'sunday': 6
        }
        days_ahead = (weekdays[weekday.lower()] - datetime.now().weekday()) % 7
        if days_ahead == 0:
            days_ahead = 7
        return self._parse_time(time_str, days_ahead=days_ahead)

    def _parse_time_today(self, time_str: str) -> datetime:
        """Parse time string for today."""
        return self._parse_time(time_str, days_ahead=0)

    def _parse_time(self, time_str: str, days_ahead: int) -> datetime:
        """Parse time string into datetime object."""
        # Remove any extra spaces and convert to lowercase
        time_str = time_str.strip().lower()
        
        # Handle different time formats
        if ':' in time_str:
            hour, minute = map(int, time_str.replace('am', '').replace('pm', '').split(':'))
        else:
            hour = int(time_str.replace('am', '').replace('pm', ''))
            minute = 0

        # Handle AM/PM
        if 'pm' in time_str and hour < 12:
            hour += 12
        elif 'am' in time_str and hour == 12:
            hour = 0

        # Create datetime object
        now = datetime.now()
        return datetime(
            year=now.year,
            month=now.month,
            day=now.day,
            hour=hour,
            minute=minute
        ) + timedelta(days=days_ahead)

    def generate_agenda_summary(self, events: List[dict]) -> str:
        """Generate a natural language summary of the daily agenda."""
        if not events:
            return "You have no events scheduled for today."

        # Sort events by start time
        sorted_events = sorted(events, key=lambda x: x['start']['dateTime'])

        # Generate summary
        summary = "Here's your agenda for today:\n\n"
        for event in sorted_events:
            start_time = datetime.fromisoformat(event['start']['dateTime'].replace('Z', '+00:00'))
            end_time = datetime.fromisoformat(event['end']['dateTime'].replace('Z', '+00:00'))
            
            summary += f"• {start_time.strftime('%I:%M %p')} - {end_time.strftime('%I:%M %p')}: {event['summary']}\n"
            if event.get('location'):
                summary += f"  Location: {event['location']}\n"
            if event.get('description'):
                summary += f"  Note: {event['description']}\n"
            summary += "\n"

        return summary

    def suggest_time_slots(self, busy_slots: List[dict], duration_minutes: int) -> str:
        """Generate natural language suggestions for available time slots."""
        if not busy_slots:
            return "You have no events scheduled for this time period."

        # Find gaps between events
        gaps = []
        for i in range(len(busy_slots) - 1):
            current_end = busy_slots[i]['end']
            next_start = busy_slots[i + 1]['start']
            gap_duration = (next_start - current_end).total_seconds() / 60

            if gap_duration >= duration_minutes:
                gaps.append({
                    'start': current_end,
                    'end': next_start,
                    'duration': gap_duration
                })

        if not gaps:
            return "There are no suitable time slots available for the requested duration."

        # Generate suggestions
        suggestions = "Here are some available time slots:\n\n"
        for gap in gaps:
            suggestions += f"• {gap['start'].strftime('%I:%M %p')} - {gap['end'].strftime('%I:%M %p')} "
            suggestions += f"(Duration: {int(gap['duration'])} minutes)\n"

        return suggestions 