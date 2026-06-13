const BASE = "/api";

function getToken() {
  return localStorage.getItem("ebm-token");
}

async function apiFetch(url, { timeoutMs = 60000, ...options } = {}) {
  const controller = new AbortController();
  const timerId = setTimeout(() => controller.abort(), timeoutMs);

  const token = getToken();
  const headers = {
    "Content-Type": "application/json",
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...options.headers,
  };

  try {
    const res = await fetch(BASE + url, {
      ...options,
      headers,
      signal: controller.signal,
    });
    clearTimeout(timerId);

    if (!res.ok) {
      const text = await res.text();
      const err = new Error(text || `HTTP ${res.status}`);
      err.status = res.status;
      throw err;
    }
    if (res.status === 204) return null;

    const contentType = res.headers.get("content-type") || "";
    return contentType.includes("application/json") ? res.json() : res.text();
  } catch (err) {
    clearTimeout(timerId);
    throw err;
  }
}

export const sendMessage = (query, sessionId = null) =>
  apiFetch("/chat", {
    timeoutMs: 120000,
    method: "POST",
    body: JSON.stringify({ query, session_id: sessionId }),
  });

export const listSessions = () => apiFetch("/sessions");

export const getSessionMessages = (sessionId) =>
  apiFetch(`/sessions/${sessionId}/messages`);

export const deleteSession = (sessionId) =>
  apiFetch(`/sessions/${sessionId}`, { method: "DELETE" });

export const renameSession = (sessionId, title) =>
  apiFetch(`/sessions/${sessionId}`, {
    method: "PATCH",
    body: JSON.stringify({ title }),
  });

// Returns { access_token, user }
export const loginUser = (identifier, password) =>
  apiFetch("/login", {
    method: "POST",
    body: JSON.stringify({ identifier, password }),
  });

// Returns created user object
export const registerUser = (username, email, password) =>
  apiFetch("/users", {
    method: "POST",
    body: JSON.stringify({ username, email, password }),
  });

export const deleteAllSessions = async () => {
  const sessions = await listSessions();
  await Promise.all(sessions.map((s) => deleteSession(s.id)));
};

export const exportAllSessions = async () => {
  const sessions = await listSessions();
  const withMessages = await Promise.all(
    sessions.map(async (s) => {
      const messages = await getSessionMessages(s.id);
      return { ...s, messages };
    })
  );
  return withMessages;
};
