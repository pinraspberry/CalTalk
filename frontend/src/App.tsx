import React, { useEffect, useState } from "react";
import ChatInterface from "./components/ChatInterface";
import CalendarView from "./components/CalendarView";
import { getDailyAgenda } from "./api/calendarApi";
import { CalendarEvent } from "./types/event";

const App: React.FC = () => {
  const [events, setEvents] = useState<CalendarEvent[]>([]);
  const [newestEventId, setNewestEventId] = useState<string | undefined>(undefined);

  const fetchEvents = async () => {
    try {
      const res = await getDailyAgenda();
      setEvents(res.data.events || []);
    } catch (err) {
      setEvents([]);
    }
  };

  useEffect(() => {
    fetchEvents();
  }, []);

  return (
    <div className="min-h-screen bg-gradient-to-br from-pink-50 via-blue-50 to-purple-50 flex flex-col font-sans">
      {/* Header */}
      <header className="w-full py-6 px-8 bg-gradient-to-r from-pink-200 via-blue-200 to-purple-200 shadow-md flex items-center gap-4">
        <div className="bg-white/40 rounded-xl p-2">
          <svg width="32" height="32" viewBox="0 0 24 24" fill="none"><circle cx="12" cy="12" r="10" fill="#a78bfa"/><path d="M8 12l2 2 4-4" stroke="#fff" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/></svg>
        </div>
        <div>
          <h1 className="text-2xl font-bold text-indigo-700 tracking-tight drop-shadow">CalTalk</h1>
          <p className="text-sm text-indigo-400">Your AI Calendar Assistant</p>
        </div>
      </header>
      {/* Main Content */}
      <main className="flex-1 flex flex-col md:flex-row gap-6 p-6 max-w-7xl mx-auto w-full">
        {/* Chat */}
        <section className="flex-1 bg-white/80 rounded-2xl shadow-xl border border-white/60 flex flex-col overflow-hidden min-h-[500px]">
          <div className="bg-gradient-to-r from-pink-200 via-blue-200 to-purple-200 p-4">
            <h2 className="text-lg font-semibold text-indigo-700">Chat with CalTalk</h2>
            <p className="text-indigo-400 text-xs mt-1">Ask me to schedule, modify, or delete events</p>
          </div>
          <div className="flex-1 flex flex-col">
            <ChatInterface onEventCreated={fetchEvents} />
          </div>
        </section>
        {/* Calendar */}
        <section className="flex-1 bg-white/80 rounded-2xl shadow-xl border border-white/60 flex flex-col overflow-hidden min-h-[500px]">
          <div className="bg-gradient-to-r from-purple-200 via-blue-200 to-pink-200 p-4">
            <h2 className="text-lg font-semibold text-indigo-700">Your Calendar</h2>
            <p className="text-purple-400 text-xs mt-1">See your upcoming events</p>
          </div>
          <div className="flex-1 p-2">
            <CalendarView events={events} newestEventId={newestEventId} />
          </div>
        </section>
      </main>
      {/* Footer */}
      <footer className="text-center py-4 text-slate-400 text-xs">
        <p>© {new Date().getFullYear()} CalTalk • Creative AI Calendar UI</p>
      </footer>
    </div>
  );
};

export default App;