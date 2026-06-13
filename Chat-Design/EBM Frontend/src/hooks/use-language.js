import { useState, useEffect } from "react";

const KEY   = "ebm-language";
const EVENT = "ebm-language-change";
const read  = () => (typeof window !== "undefined" ? localStorage.getItem(KEY) || "en" : "en");

export const useLanguage = () => {
  const [lang, setLangState] = useState(read);

  useEffect(() => {
    const handler = () => setLangState(read());
    window.addEventListener(EVENT, handler);
    window.addEventListener("storage", handler);
    return () => {
      window.removeEventListener(EVENT, handler);
      window.removeEventListener("storage", handler);
    };
  }, []);

  const setLang = (value) => {
    localStorage.setItem(KEY, value);
    setLangState(value);
    window.dispatchEvent(new Event(EVENT));
  };

  return [lang, setLang];
};
