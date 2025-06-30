from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import os
from dotenv import load_dotenv
from app.services.nlp import NLPService
from app.services.calendar import CalendarService

# Initialize services
nlp_service = NLPService()
calendar_service = CalendarService()

# Load environment variables
load_dotenv()

app = FastAPI(
    title="Personal Calendar Assistant",
    description="An intelligent calendar management system with natural language processing",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Models
class Event(BaseModel):
    title: str
    start_time: datetime
    end_time: datetime
    description: Optional[str] = None
    priority: Optional[str] = "medium"
    location: Optional[str] = None
    attendees: Optional[List[str]] = None

class UserInput(BaseModel):
    text: str

# Routes
@app.get("/")
async def root():
    return {"message": "Welcome to Personal Calendar Assistant API"}

# @app.post("/events/create")
# async def create_event(event: Event):
#     try:
#         # Convert structured event to natural language for OpenAI processing
#         event_description = f"Create event: {event.title} from {event.start_time} to {event.end_time}"
#         if event.description:
#             event_description += f" with description: {event.description}"
#         if event.location:
#             event_description += f" at {event.location}"
#         if event.attendees:
#             event_description += f" with attendees: {', '.join(event.attendees)}"
        
#         # Send to NLP service for enhanced parsing
#         event_intent = nlp_service.parse_event_intent(event_description)
        
#         # Create the calendar event with enhanced data
#         event_data = {
#             'title': event_intent.title or event.title,
#             'start_time': event_intent.start_time or event.start_time,
#             'end_time': event_intent.end_time or event.end_time,
#             'description': event_intent.description or event.description,
#             'location': event_intent.location or event.location,
#             'attendees': event_intent.attendees or event.attendees,
#             'priority': event_intent.priority or event.priority
#         }
        
#         created_event = calendar_service.create_event(event_data)
#         return {"message": "Event created successfully", "event": created_event}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))
    
@app.post("/events/natural")
async def create_event_natural(user_input: UserInput):
    try:
        # Parse natural language into structured event data
        event_intent = nlp_service.parse_event_intent(user_input.text)
        
        # Create the calendar event
        event_data = {
            'title': event_intent.title,
            'start_time': event_intent.start_time,
            'end_time': event_intent.end_time,
            'description': event_intent.description,
            'location': event_intent.location,
            'attendees': event_intent.attendees,
            'priority': event_intent.priority
        }
        
        created_event = calendar_service.create_event(event_data)
        return {"message": "Event created successfully", "event": created_event}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/events/daily")
async def get_daily_agenda(date: Optional[str] = None):
    try:
        if date:
            # Parse the date string
            try:
                parsed_date = datetime.fromisoformat(date)
            except ValueError:
                # Try parsing as date only
                parsed_date = datetime.strptime(date, "%Y-%m-%d")
        else:
            parsed_date = datetime.now()
        
        events = calendar_service.get_daily_agenda(parsed_date)
        return {"message": "Daily agenda retrieved", "events": events, "date": parsed_date.isoformat()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/events/conflicts")
async def check_conflicts(start_time: datetime, end_time: datetime):
    try:
        # TODO: Implement conflict detection
        return {"message": "Checking for conflicts", "start_time": start_time, "end_time": end_time}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/events/{event_id}")
async def delete_event(event_id: str):
    try:
        calendar_service.delete_event(event_id)
        return {"message": "Event deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 