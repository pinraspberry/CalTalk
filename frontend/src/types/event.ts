export interface CalendarEvent {
  id?: string;
  title: string;
  start_time: string; // ISO string
  end_time: string;   // ISO string
  description?: string;
  priority?: string;
  location?: string;
  attendees?: string[];
}