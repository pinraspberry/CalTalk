from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from ..config import get_settings
from .calendar import CalendarService
from .nlp import NLPService

class SchedulerService:
    def __init__(self):
        self.settings = get_settings()
        self.calendar_service = CalendarService()
        self.nlp_service = NLPService()

    def schedule_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Schedule a task in the calendar based on priority and available time."""
        # Get the duration of the task
        duration_minutes = task.get('duration_minutes', self.settings.DEFAULT_EVENT_DURATION)
        
        # Get the preferred date
        preferred_date = task.get('preferred_date', datetime.now().date())
        
        # Find available time slots
        free_slots = self.calendar_service.find_free_slots(
            datetime.combine(preferred_date, datetime.min.time()),
            duration_minutes
        )
        
        if not free_slots:
            # If no slots available on preferred date, try next day
            next_date = preferred_date + timedelta(days=1)
            free_slots = self.calendar_service.find_free_slots(
                datetime.combine(next_date, datetime.min.time()),
                duration_minutes
            )
        
        if not free_slots:
            raise ValueError("No suitable time slots found for the task")
        
        # Select the best time slot based on priority
        selected_slot = self._select_best_slot(free_slots, task.get('priority', 'medium'))
        
        # Create the calendar event
        event_data = {
            'title': task['title'],
            'start_time': selected_slot['start'],
            'end_time': selected_slot['end'],
            'description': task.get('description', ''),
            'priority': task.get('priority', 'medium')
        }
        
        return self.calendar_service.create_event(event_data)

    def _select_best_slot(self, free_slots: List[Dict[str, datetime]], priority: str) -> Dict[str, datetime]:
        """Select the best time slot based on priority and time of day."""
        if priority == 'high' or priority == 'urgent':
            # For high priority tasks, prefer morning slots
            morning_slots = [slot for slot in free_slots if slot['start'].hour < 12]
            if morning_slots:
                return morning_slots[0]
        
        # For medium and low priority tasks, return the first available slot
        return free_slots[0]

    def reschedule_conflicts(self, event_id: str, new_time: datetime) -> Dict[str, Any]:
        """Reschedule an event and handle any conflicts."""
        # Get the original event
        original_event = self.calendar_service.service.events().get(
            calendarId='primary',
            eventId=event_id
        ).execute()
        
        # Calculate duration
        start_time = datetime.fromisoformat(original_event['start']['dateTime'].replace('Z', '+00:00'))
        end_time = datetime.fromisoformat(original_event['end']['dateTime'].replace('Z', '+00:00'))
        duration = end_time - start_time
        
        # Check for conflicts at new time
        conflicts = self.calendar_service.check_conflicts(new_time, new_time + duration)
        
        if conflicts:
            # Find alternative time slots
            free_slots = self.calendar_service.find_free_slots(
                new_time.date(),
                int(duration.total_seconds() / 60)
            )
            
            if not free_slots:
                raise ValueError("No suitable alternative time slots found")
            
            # Select the closest available slot
            selected_slot = min(free_slots, key=lambda x: abs(x['start'] - new_time))
            new_time = selected_slot['start']
        
        # Update the event
        event_data = {
            'start_time': new_time,
            'end_time': new_time + duration
        }
        
        return self.calendar_service.update_event(event_id, event_data)

    def create_time_block(self, block_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a time block for focused work or specific activities."""
        # Validate time block data
        if 'start_time' not in block_data or 'end_time' not in block_data:
            raise ValueError("Start time and end time are required for time blocks")
        
        # Check for conflicts
        conflicts = self.calendar_service.check_conflicts(
            block_data['start_time'],
            block_data['end_time']
        )
        
        if conflicts:
            raise ValueError("Time block conflicts with existing events")
        
        # Create the time block event
        event_data = {
            'title': block_data.get('title', 'Time Block'),
            'start_time': block_data['start_time'],
            'end_time': block_data['end_time'],
            'description': block_data.get('description', ''),
            'colorId': block_data.get('color_id', '1')  # Default color
        }
        
        return self.calendar_service.create_event(event_data)

    def suggest_routine_times(self, routine_data: Dict[str, Any]) -> List[Dict[str, datetime]]:
        """Suggest optimal times for recurring routines based on existing schedule."""
        duration_minutes = routine_data.get('duration_minutes', self.settings.DEFAULT_EVENT_DURATION)
        preferred_time = routine_data.get('preferred_time')
        days_of_week = routine_data.get('days_of_week', [0, 1, 2, 3, 4])  # Monday to Friday by default
        
        suggestions = []
        current_date = datetime.now().date()
        
        # Look ahead for the next 7 days
        for _ in range(7):
            if current_date.weekday() in days_of_week:
                # Get free slots for the day
                free_slots = self.calendar_service.find_free_slots(
                    datetime.combine(current_date, datetime.min.time()),
                    duration_minutes
                )
                
                if free_slots:
                    # If preferred time is specified, try to find the closest slot
                    if preferred_time:
                        best_slot = min(
                            free_slots,
                            key=lambda x: abs(x['start'].time() - preferred_time)
                        )
                    else:
                        best_slot = free_slots[0]
                    
                    suggestions.append({
                        'date': current_date,
                        'start_time': best_slot['start'],
                        'end_time': best_slot['end']
                    })
            
            current_date += timedelta(days=1)
        
        return suggestions

    def optimize_schedule(self, date: datetime) -> List[Dict[str, Any]]:
        """Optimize the schedule for a given date based on priorities and preferences."""
        # Get all events for the date
        events = self.calendar_service.get_daily_agenda(date)
        
        # Sort events by priority
        priority_order = {priority: i for i, priority in enumerate(self.settings.PRIORITY_LEVELS)}
        sorted_events = sorted(
            events,
            key=lambda x: priority_order.get(x.get('priority', 'medium'), 0)
        )
        
        # Check for conflicts and suggest rescheduling
        optimized_schedule = []
        for event in sorted_events:
            start_time = datetime.fromisoformat(event['start']['dateTime'].replace('Z', '+00:00'))
            end_time = datetime.fromisoformat(event['end']['dateTime'].replace('Z', '+00:00'))
            
            # Check for conflicts with already optimized events
            conflicts = [
                e for e in optimized_schedule
                if (start_time < e['end_time'] and end_time > e['start_time'])
            ]
            
            if conflicts:
                # Try to reschedule the event
                try:
                    rescheduled = self.reschedule_conflicts(event['id'], start_time)
                    optimized_schedule.append({
                        'event': rescheduled,
                        'start_time': datetime.fromisoformat(rescheduled['start']['dateTime'].replace('Z', '+00:00')),
                        'end_time': datetime.fromisoformat(rescheduled['end']['dateTime'].replace('Z', '+00:00'))
                    })
                except ValueError:
                    # If rescheduling fails, keep the original time
                    optimized_schedule.append({
                        'event': event,
                        'start_time': start_time,
                        'end_time': end_time
                    })
            else:
                optimized_schedule.append({
                    'event': event,
                    'start_time': start_time,
                    'end_time': end_time
                })
        
        return optimized_schedule 