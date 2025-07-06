import React from "react";
import { Box, Typography, List, ListItem, ListItemText, Chip } from "@mui/material";
import { CalendarEvent } from "../types/event";

const Sidebar: React.FC<{ events: CalendarEvent[] }> = ({ events }) => {
  const getEventTitle = (event: CalendarEvent) => {
    return event.title || "Untitled Event";
  };

  const getEventTime = (event: CalendarEvent) => {
    const startTime = event.start_time;
    if (!startTime) return "No time specified";
    
    try {
      return new Date(startTime).toLocaleString();
    } catch {
      return startTime;
    }
  };

  return (
    <Box width={280} p={2} bgcolor="#fafafa" height="100%" borderRight="1px solid #eee">
      <Typography variant="h6" mb={2}>Upcoming Events</Typography>
      <List dense>
        {events.length === 0 ? (
          <ListItem><ListItemText primary="No upcoming events" /></ListItem>
        ) : (
          events.map((ev, idx) => (
            <ListItem key={ev.id || idx} alignItems="flex-start">
              <ListItemText
                primary={getEventTitle(ev)}
                secondary={
                  <>
                    {getEventTime(ev)}<br />
                    {ev.description}
                  </>
                }
              />
              {ev.priority && <Chip label={ev.priority} size="small" sx={{ ml: 1 }} />}
            </ListItem>
          ))
        )}
      </List>
      <Box mt={4}>
        <Typography variant="subtitle1">Suggestions</Typography>
        <ul style={{ margin: 0, paddingLeft: 18 }}>
          <li>"Schedule a 1:1 with your manager"</li>
          <li>"Plan a team lunch next Friday"</li>
        </ul>
      </Box>
    </Box>
  );
};

export default Sidebar; 