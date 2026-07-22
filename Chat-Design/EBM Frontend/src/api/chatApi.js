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

export const sendMessage = (query, sessionId = null, pdfContext = null) =>
  apiFetch("/chat", {
    timeoutMs: 120000,
    method: "POST",
    body: JSON.stringify({ query, session_id: sessionId, pdf_context: pdfContext || undefined }),
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

export const deleteAllSessions = () =>
  apiFetch("/sessions", { method: "DELETE" });

export const updateUsername = (username) =>
  apiFetch("/users/me", {
    method: "PATCH",
    body: JSON.stringify({ username }),
  });

export const uploadPdf = async (file) => {
  const token = getToken();
  const form = new FormData();
  form.append("file", file);
  const res = await fetch(`${BASE}/upload/pdf`, {
    method: "POST",
    headers: token ? { Authorization: `Bearer ${token}` } : {},
    body: form,
  });
  if (!res.ok) {
    const text = await res.text();
    const err = new Error(text || `HTTP ${res.status}`);
    err.status = res.status;
    throw err;
  }
  return res.json();
};

export const exportSessionCsv = async (sessionId, filename) => {
  const token = getToken();
  const res = await fetch(`${BASE}/sessions/${sessionId}/export`, {
    headers: token ? { Authorization: `Bearer ${token}` } : {},
  });
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  const blob = await res.blob();
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  a.click();
  URL.revokeObjectURL(url);
};
