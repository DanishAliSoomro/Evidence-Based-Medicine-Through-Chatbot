import { useState } from "react";

const KEY = "ebm-language";
const EVENT = "ebm-language-change";
const read = () =>
  typeof window !== "undefined" ? localStorage.getItem(KEY) || "en" : "en";

export const useLanguage = () => {
  const [lang, setLangState] = useState(read);

  const setLang = (value) => {
    localStorage.setItem(KEY, value);
    setLangState(value);
    window.dispatchEvent(new Event(EVENT));
  };

  return [lang, setLang];
};
