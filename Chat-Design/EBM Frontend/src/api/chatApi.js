const BASE = "/api";

async function apiFetch(url, { timeoutMs = 60000, ...options } = {}) {
  const controller = new AbortController();
  const timerId = setTimeout(() => controller.abort(), timeoutMs);
  try {
    const res = await fetch(BASE + url, {
      headers: { "Content-Type": "application/json" },
      signal: controller.signal,
      ...options,
    });
    clearTimeout(timerId);
    if (!res.ok) {
      const text = await res.text();
      throw new Error(text || `HTTP ${res.status}`);
    }
    if (res.status === 204) {
      return null;
    }

    const contentType = res.headers.get("content-type") || "";
    if (contentType.includes("application/json")) {
      return res.json();
    }

    return res.text();
  } catch (err) {
    clearTimeout(timerId);
    throw err;
  }
}

export const sendMessage = (query, sessionId = null, ownerId = null) =>
  apiFetch("/chat", {
    timeoutMs: 120000,
    method: "POST",
    body: JSON.stringify({ query, session_id: sessionId, owner_id: ownerId }),
  });

export const listSessions = (ownerId = null) =>
  apiFetch(ownerId != null ? `/sessions?owner_id=${ownerId}` : "/sessions");

export const getSessionMessages = (sessionId) =>
  apiFetch(`/sessions/${sessionId}/messages`);

export const deleteSession = (sessionId) =>
  apiFetch(`/sessions/${sessionId}`, { method: "DELETE" });

export const renameSession = (sessionId, title) =>
  apiFetch(`/sessions/${sessionId}`, {
    method: "PATCH",
    body: JSON.stringify({ title }),
  });

// POST /api/login — identifier can be username or email
export const loginUser = (identifier, password) =>
  apiFetch("/login", {
    method: "POST",
    body: JSON.stringify({ identifier, password }),
  });

// POST /api/users — register new user
export const registerUser = (username, email, password) =>
  apiFetch("/users", {
    method: "POST",
    body: JSON.stringify({ username, email, password }),
  });


export const deleteAllSessions = async (ownerId = null) => {
  const sessions = await listSessions(ownerId);
  await Promise.all(sessions.map((s) => deleteSession(s.id)));
};

export const exportAllSessions = async (ownerId = null) => {
  const sessions = await listSessions(ownerId);
  const active = sessions.filter((s) => !s.is_deleted);
  const withMessages = await Promise.all(
    active.map(async (s) => {
      const messages = await getSessionMessages(s.id);
      return { ...s, messages };
    })
  );
  return withMessages;
};
