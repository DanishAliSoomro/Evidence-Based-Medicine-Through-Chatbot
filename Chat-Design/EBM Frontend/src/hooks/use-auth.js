import { useState } from "react";

const USER_KEY  = "ebm-user";
const TOKEN_KEY = "ebm-token";

const readUser  = () => { try { const s = localStorage.getItem(USER_KEY);  return s ? JSON.parse(s) : null; } catch { return null; } };
const readToken = () => localStorage.getItem(TOKEN_KEY) ?? null;

export const useAuth = () => {
  const [user,  setUser]  = useState(readUser);
  const [token, setToken] = useState(readToken);

  const login = (userData, accessToken) => {
    localStorage.setItem(USER_KEY,  JSON.stringify(userData));
    localStorage.setItem(TOKEN_KEY, accessToken);
    setUser(userData);
    setToken(accessToken);
  };

  const logout = () => {
    localStorage.removeItem(USER_KEY);
    localStorage.removeItem(TOKEN_KEY);
    setUser(null);
    setToken(null);
  };

  return { user, token, login, logout };
};

export const getStoredUser  = () => readUser();
export const getStoredToken = () => readToken();
