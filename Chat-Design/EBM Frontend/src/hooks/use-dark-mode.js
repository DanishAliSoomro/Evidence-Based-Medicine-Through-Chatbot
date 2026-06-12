import { useEffect, useState } from "react";
const KEY = "ebm-dark-mode";
const EVENT = "ebm-dark-mode-change";
const read = () => typeof window !== "undefined" && localStorage.getItem(KEY) === "true";
export const useDarkMode = () => {
    const [enabled, setEnabledState] = useState(read);
    useEffect(() => {
        const handler = () => setEnabledState(read());
        window.addEventListener(EVENT, handler);
        window.addEventListener("storage", handler);
        return () => {
            window.removeEventListener(EVENT, handler);
            window.removeEventListener("storage", handler);
        };
    }, []);
    const setEnabled = (value) => {
        localStorage.setItem(KEY, String(value));
        setEnabledState(value);
        window.dispatchEvent(new Event(EVENT));
    };
    return [enabled, setEnabled];
};
