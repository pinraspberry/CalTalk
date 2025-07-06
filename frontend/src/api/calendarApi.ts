import axios from "axios";

const API_BASE = "http://localhost:8000";

// // Unified function that sends structured data through NLP
// export const createEvent = (event: any) =>
//   axios.post(`${API_BASE}/events/create`, event);

// Keep natural language function
export const createEventNatural = async (text: string) => {
  try {
    return await axios.post(`${API_BASE}/events/natural`, { text });
  } catch (error: any) {
    console.error('Create event error:', error.response?.data || error.message);
    throw error;
  }
  
};

export const getDailyAgenda = (date?: string) =>
  axios.get(`${API_BASE}/events/daily`, { params: { date } });

export const deleteEvent = async (eventId: string) => {
  try {
    return await axios.delete(`${API_BASE}/events/${eventId}`);
  } catch (error: any) {
    console.error('Delete event error:', error.response?.data || error.message);
    throw error;
  }
};