import { useState, useCallback, useEffect, useRef } from "react";
import { useNavigate, useParams } from "react-router-dom";
import ChatSidebar from "@/components/ChatSidebar";
import CollapsedSidebar from "@/components/CollapsedSidebar";
import ChatMain from "@/components/ChatMain";
import { useDarkMode } from "@/hooks/use-dark-mode";
import { useAuth } from "@/hooks/use-auth";
import { toast } from "@/hooks/use-toast";
import * as api from "@/api/chatApi";

const toConv = (session) => ({
  id: session.id,
  title: session.title,
  preview: session.title,
  timestamp: new Date(session.created_at),
});

const toMsg = (msg) => ({
  id: String(msg.id),
  role: msg.role,
  content: msg.content,
  timestamp: new Date(msg.timestamp),
});

const Index = () => {
  const navigate = useNavigate();
  const { sessionId: sessionIdParam } = useParams();
  const { user } = useAuth();
  const [darkMode] = useDarkMode();

  const [messages, setMessages] = useState([]);
  const [conversations, setConversations] = useState([]);
  const [activeChat, setActiveChat] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const currentSessionId = useRef(null);

  // Redirect to login if not authenticated
  useEffect(() => {
    if (!user) navigate("/login", { replace: true });
  }, [user, navigate]);

  // Load this user's sessions on mount
  useEffect(() => {
    if (!user) return;
    api.listSessions(user.id)
      .then((sessions) => setConversations(sessions.map(toConv)))
      .catch(() => {});
  }, [user?.id]);

  // Restore session from URL (direct link or page refresh)
  useEffect(() => {
    if (!sessionIdParam || !user) return;
    const sid = parseInt(sessionIdParam, 10);
    if (isNaN(sid) || currentSessionId.current === sid) return;
    currentSessionId.current = sid;
    setActiveChat(sid);
    api.getSessionMessages(sid)
      .then((msgs) => setMessages(msgs.map(toMsg)))
      .catch(() => {});
  }, [sessionIdParam, user?.id]);

  const refreshSessions = useCallback(async () => {
    if (!user) return;
    try {
      const sessions = await api.listSessions(user.id);
      setConversations(sessions.map(toConv));
    } catch {}
  }, [user?.id]);

  const handleNewChat = () => {
    setMessages([]);
    setActiveChat(null);
    currentSessionId.current = null;
    navigate("/", { replace: true });
  };

  const handleSendMessage = useCallback(async (content) => {
    setMessages((prev) => [...prev, {
      id: `user-${Date.now()}`,
      role: "user",
      content,
      timestamp: new Date(),
    }]);
    setIsLoading(true);

    try {
      const data = await api.sendMessage(content, currentSessionId.current, user?.id ?? null);
      currentSessionId.current = data.session_id;
      setActiveChat(data.session_id);
      // replaceState avoids remounting Index when route changes from / to /chat/:id
      window.history.replaceState(null, "", `/chat/${data.session_id}`);

      setMessages((prev) => [...prev, {
        id: `assistant-${Date.now()}`,
        role: "assistant",
        content: data.answer,
        timestamp: new Date(),
      }]);

      await refreshSessions();
    } catch (err) {
      const isOffline =
        err?.name === "AbortError" ||
        err?.message?.includes("Failed to fetch") ||
        err?.message?.includes("NetworkError");

      setMessages((prev) => [...prev, {
        id: `error-${Date.now()}`,
        role: "assistant",
        content: isOffline
          ? "**API not connected.** The backend server is not reachable."
          : `**Error:** ${err?.message || "Something went wrong. Please try again."}`,
        timestamp: new Date(),
      }]);
    } finally {
      setIsLoading(false);
    }
  }, [user?.id, refreshSessions]);

  const handleSelectChat = useCallback(async (id) => {
    setActiveChat(id);
    currentSessionId.current = id;
    window.history.replaceState(null, "", `/chat/${id}`);
    try {
      const msgs = await api.getSessionMessages(id);
      setMessages(msgs.map(toMsg));
    } catch {
      toast({ title: "Error", description: "Failed to load conversation.", variant: "destructive" });
    }
  }, []);

  const handleDeleteChat = useCallback(async (id) => {
    try {
      await api.deleteSession(id);
      setConversations((prev) => prev.filter((c) => c.id !== id));
      if (activeChat === id) {
        setMessages([]);
        setActiveChat(null);
        currentSessionId.current = null;
        navigate("/", { replace: true });
      }
    } catch {
      toast({ title: "Error", description: "Failed to delete conversation.", variant: "destructive" });
    }
  }, [activeChat, navigate]);

  const handleBookmark = useCallback((id) => {
    setMessages((prev) =>
      prev.map((msg) => (msg.id === id ? { ...msg, bookmarked: !msg.bookmarked } : msg))
    );
  }, []);

  const toggleSidebar = () => setSidebarOpen((prev) => !prev);

  if (!user) return null;

  return (
    <div className={darkMode ? "dark" : ""}>
      <div className="flex h-screen overflow-hidden bg-background text-foreground">
        {sidebarOpen ? (
          <ChatSidebar
            onNewChat={handleNewChat}
            conversations={conversations}
            onSelectChat={handleSelectChat}
            onDeleteChat={handleDeleteChat}
            activeChat={activeChat}
            onClose={toggleSidebar}
            currentUser={user}
          />
        ) : (
          <CollapsedSidebar
            onOpenSidebar={toggleSidebar}
            onNewChat={handleNewChat}
            onSearchChats={toggleSidebar}
          />
        )}
        <ChatMain
          messages={messages}
          onSendMessage={handleSendMessage}
          onBookmark={handleBookmark}
          isLoading={isLoading}
          sidebarOpen={sidebarOpen}
          onToggleSidebar={toggleSidebar}
        />
      </div>
    </div>
  );
};

export default Index;
