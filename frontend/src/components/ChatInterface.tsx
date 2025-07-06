import React, { useState, useRef, useEffect } from "react";
import { createEventNatural, deleteEvent } from "../api/calendarApi";

interface ChatMessage {
  id: number;
  sender: "user" | "assistant";
  text: string;
  eventId?: string;
  editable?: boolean;
}

const ChatInterface: React.FC<{ onEventCreated?: () => void }> = ({ onEventCreated }) => {
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState<ChatMessage[]>([{
    id: 1,
    sender: "assistant",
    text: "Hello! I'm CalTalk, your AI calendar assistant. I can help you schedule meetings, create events, or manage your calendar. Try saying something like 'Schedule a team meeting tomorrow at 2pm' or 'What do I have on Friday?'"
  }]);
  const [isSending, setIsSending] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSend = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!input.trim()) return;
    const userMsg: ChatMessage = {
      id: Date.now(),
      sender: "user",
      text: input,
    };
    setMessages((msgs) => [...msgs, userMsg]);
    setInput("");
    setIsSending(true);
    try {
      const res = await createEventNatural(userMsg.text);
      const event = res.data.event;
      const assistantMsg: ChatMessage = {
        id: Date.now() + 1,
        sender: "assistant",
        text: event
          ? `Event '${event.summary || event.title || "(unknown)"}' created for ${event.start?.dateTime || event.start_time || "(unknown time)"}.`
          : res.data.message || "I couldn't create the event.",
        eventId: event?.id,
        editable: true,
      };
      setMessages((msgs) => [...msgs, assistantMsg]);
      if (onEventCreated) onEventCreated();
    } catch (err: any) {
      setMessages((msgs) => [
        ...msgs,
        {
          id: Date.now() + 2,
          sender: "assistant",
          text: "Sorry, I couldn't create the event. Please try again.",
        },
      ]);
    } finally {
      setIsSending(false);
    }
  };

  return (
    <div className="flex flex-col h-full">
      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-gradient-to-br from-pink-50 via-blue-50 to-purple-50">
        {messages.map((msg) => (
          <div
            key={msg.id}
            className={`flex ${msg.sender === "user" ? "justify-end" : "justify-start"}`}
          >
            <div
              className={`rounded-2xl px-4 py-3 max-w-[75%] shadow text-sm font-medium whitespace-pre-line ${
                msg.sender === "user"
                  ? "bg-gradient-to-r from-pink-200 via-blue-200 to-purple-200 text-indigo-700 rounded-br-md"
                  : "bg-white/80 text-indigo-700 border border-indigo-100 rounded-bl-md"
              }`}
            >
              {msg.text}
            </div>
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>
      {/* Input */}
      <form
        onSubmit={handleSend}
        className="flex gap-2 p-4 border-t border-indigo-100 bg-white/80"
      >
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Type your message... (e.g., 'Schedule a meeting tomorrow at 2pm')"
          className="flex-1 px-4 py-3 border border-indigo-100 rounded-xl focus:outline-none focus:ring-2 focus:ring-pink-200 bg-white/90 backdrop-blur-sm text-indigo-700"
          disabled={isSending}
        />
        <button
          type="submit"
          disabled={!input.trim() || isSending}
          className="px-4 py-3 bg-gradient-to-r from-pink-300 via-blue-300 to-purple-300 text-indigo-700 rounded-xl hover:from-pink-400 hover:to-purple-400 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 shadow-lg hover:shadow-xl font-semibold"
        >
          Send
        </button>
      </form>
    </div>
  );
};

export default ChatInterface; 