import React from "react";
import { Box, Button, ButtonGroup } from "@mui/material";

const FILTERS = [
  { label: "All", value: "all" },
  { label: "Work", value: "work" },
  { label: "Personal", value: "personal" },
  { label: "Important", value: "high" },
];

const FilterBar: React.FC<{
  selected: string;
  onChange: (filter: string) => void;
}> = ({ selected, onChange }) => (
  <Box mb={2} display="flex" justifyContent="center">
    <ButtonGroup variant="outlined">
      {FILTERS.map(f => (
        <Button
          key={f.value}
          variant={selected === f.value ? "contained" : "outlined"}
          onClick={() => onChange(f.value)}
        >
          {f.label}
        </Button>
      ))}
    </ButtonGroup>
  </Box>
);

export default FilterBar; 