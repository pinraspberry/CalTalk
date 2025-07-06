import React, { useState } from "react";
import { TextField, Button, Box, Typography } from "@mui/material";
import { createEventNatural } from "../api/calendarApi";

const NaturalEventInput: React.FC<{ onEventCreated?: () => void }> = ({ onEventCreated }) => {
  const [input, setInput] = useState("");
  const [response, setResponse] = useState<any>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const res = await createEventNatural(input);
    setResponse(res.data);
    setInput("");
    if (onEventCreated) onEventCreated();
  };

  return (
    <Box mb={3}>
      <form onSubmit={handleSubmit}>
        <TextField
          label="Natural Language Event"
          value={input}
          onChange={e => setInput(e.target.value)}
          fullWidth
          placeholder="e.g. Schedule a call with Riya tomorrow at 3 PM"
        />
        <Button type="submit" variant="contained" sx={{ mt: 2 }}>
          Create Event
        </Button>
      </form>
      {response && (
        <Box mt={2}>
          <Typography variant="body2" color="textSecondary">
            {JSON.stringify(response, null, 2)}
          </Typography>
        </Box>
      )}
    </Box>
  );
};

export default NaturalEventInput; 