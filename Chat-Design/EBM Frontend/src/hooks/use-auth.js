import { useState } from "react";

const STORAGE_KEY = "ebm-user";

const readUser = () => {
  try {
    const stored = localStorage.getItem(STORAGE_KEY);
    return stored ? JSON.parse(stored) : null;
  } catch {
    return null;
  }
};

export const useAuth = () => {
  const [user, setUser] = useState(readUser);

  const login = (userData) => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(userData));
    setUser(userData);
  };

  const logout = () => {
    localStorage.removeItem(STORAGE_KEY);
    setUser(null);
  };

  return { user, login, logout };
};

// Synchronous read — safe to call outside React (e.g. in API handlers)
export const getStoredUser = () => readUser();
