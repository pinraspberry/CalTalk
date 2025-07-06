import React, { useRef, useEffect } from "react";
import FullCalendar from "@fullcalendar/react";
import dayGridPlugin from "@fullcalendar/daygrid";
import timeGridPlugin from "@fullcalendar/timegrid";
import interactionPlugin from "@fullcalendar/interaction";
import { CalendarEvent } from "../types/event";

interface CalendarViewProps {
  events: CalendarEvent[];
  newestEventId?: string;
}

function getEventColor(priority?: string): string {
  switch (priority) {
    case "high":
    case "urgent":
      return "#f472b6"; // pink-400
    case "medium":
      return "#818cf8"; // indigo-400
    case "low":
      return "#6ee7b7"; // green-300
    default:
      return "#a5b4fc"; // indigo-200
  }
}

const CalendarView: React.FC<CalendarViewProps> = ({ events, newestEventId }) => {
  const calendarRef = useRef<FullCalendar | null>(null);

  useEffect(() => {
    if (newestEventId && calendarRef.current) {
      // Optionally scroll to or highlight the newest event
      // FullCalendar doesn't have direct scroll-to-event, but we can highlight
      // This is a placeholder for animation/highlight logic
    }
  }, [newestEventId, events]);

  return (
    <div className="h-full w-full bg-gradient-to-br from-white via-pink-50 to-blue-50 rounded-2xl p-2 shadow">
      <FullCalendar
        ref={calendarRef}
        plugins={[dayGridPlugin, timeGridPlugin, interactionPlugin]}
        initialView="timeGridWeek"
        headerToolbar={{
          left: "prev,next today",
          center: "title",
          right: "dayGridDay,timeGridWeek,dayGridMonth",
        }}
        events={events.map(ev => ({
          id: ev.id || (ev.title + ev.start_time),
          title: ev.title,
          start: ev.start_time,
          end: ev.end_time,
          backgroundColor: getEventColor(ev.priority),
          borderColor: newestEventId && (ev.id || (ev.title + ev.start_time)) === newestEventId ? "#f59e42" : undefined,
          description: ev.description,
        }))}
        eventContent={renderEventContent}
        height="auto"
      />
    </div>
  );
};

function renderEventContent(eventInfo: any) {
  return (
    <div className="px-2 py-1 rounded-lg bg-white/80 border border-pink-100">
      <b className="text-xs font-semibold text-indigo-700">{eventInfo.event.title}</b>
      {eventInfo.event.extendedProps.description && (
        <div className="text-xs text-pink-400 mt-0.5">{eventInfo.event.extendedProps.description}</div>
      )}
    </div>
  );
}

export default CalendarView; 