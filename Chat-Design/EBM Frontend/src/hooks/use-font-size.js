import { useState } from "react";

const KEY = "ebm-font-size";
const read = () =>
  typeof window !== "undefined" ? localStorage.getItem(KEY) || "medium" : "medium";

export const useFontSize = () => {
  const [size, setSizeState] = useState(read);

  const setSize = (value) => {
    localStorage.setItem(KEY, value);
    setSizeState(value);
  };

  return [size, setSize];
};
