import { useState, useEffect, useRef } from "react";
import { Download, Trash2, FileText, Search, X } from "lucide-react";
import { useLanguage } from "@/hooks/use-language";
import { toast } from "@/hooks/use-toast";
import { listSessions, exportSessionCsv, deleteAllSessions } from "@/api/chatApi";
import { Section, Row, Button } from "./SettingsShared";

const SessionPickerModal = ({ sessions, onSelect, onClose, isUrdu }) => {
  const [query, setQuery] = useState("");
  const inputRef = useRef(null);

  useEffect(() => {
    inputRef.current?.focus();
    const handler = (e) => { if (e.key === "Escape") onClose(); };
    window.addEventListener("keydown", handler);
    return () => window.removeEventListener("keydown", handler);
  }, [onClose]);

  const filtered = sessions.filter((s) =>
    (s.title ?? "").toLowerCase().includes(query.toLowerCase())
  );

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm"
      onClick={onClose}
    >
      <div
        className="w-full max-w-md mx-4 rounded-2xl border border-border bg-card shadow-2xl flex flex-col overflow-hidden"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="flex items-center justify-between px-4 pt-4 pb-2">
          <p className="font-semibold text-foreground">
            {isUrdu ? "سیشن منتخب کریں" : "Select a session"}
          </p>
          <button
            onClick={onClose}
            className="p-1.5 rounded-md hover:bg-muted text-muted-foreground hover:text-foreground transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Search */}
        <div className="px-4 pb-2">
          <div className="flex items-center gap-2 px-3 py-2 rounded-lg border border-input bg-background">
            <Search className="w-4 h-4 text-muted-foreground flex-shrink-0" />
            <input
              ref={inputRef}
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder={isUrdu ? "گفتگو تلاش کریں…" : "Search conversations…"}
              className="flex-1 bg-transparent text-sm text-foreground placeholder:text-muted-foreground focus:outline-none"
            />
            {query && (
              <button onClick={() => setQuery("")}>
                <X className="w-3.5 h-3.5 text-muted-foreground hover:text-foreground" />
              </button>
            )}
          </div>
        </div>

        {/* Session list */}
        <div className="overflow-y-auto max-h-72 px-2 pb-3">
          {filtered.length === 0 ? (
            <p className="text-sm text-muted-foreground text-center py-6">
              {isUrdu ? "کوئی نتیجہ نہیں ملا۔" : "No sessions found."}
            </p>
          ) : (
            filtered.map((session) => (
              <button
                key={session.id}
                onClick={() => onSelect(session)}
                className="w-full text-left px-3 py-2.5 rounded-lg hover:bg-muted transition-colors flex items-center gap-3 group"
              >
                <div className="w-8 h-8 rounded-lg bg-primary/10 flex items-center justify-center flex-shrink-0">
                  <FileText className="w-4 h-4 text-primary" />
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-foreground truncate">
                    {session.title ?? `Session ${session.id}`}
                  </p>
                  <p className="text-xs text-muted-foreground">
                    {new Date(session.created_at).toLocaleDateString()}
                  </p>
                </div>
                <Download className="w-4 h-4 text-muted-foreground opacity-0 group-hover:opacity-100 transition-opacity flex-shrink-0" />
              </button>
            ))
          )}
        </div>
      </div>
    </div>
  );
};

const Chat = () => {
  const [language] = useLanguage();
  const [sessions, setSessions]       = useState([]);
  const [showPicker, setShowPicker]   = useState(false);
  const [downloading, setDownloading] = useState(false);
  const [clearing, setClearing]       = useState(false);
  const isUrdu = language === "ur";
  const s = (en, ur) => (isUrdu ? ur : en);

  useEffect(() => {
    listSessions().then(setSessions).catch(() => {});
  }, []);

  const handleSelect = async (session) => {
    setShowPicker(false);
    setDownloading(true);
    try {
      const filename = `ebm-${(session.title ?? `session-${session.id}`).slice(0, 30).replace(/\s+/g, "-")}-${new Date().toISOString().slice(0, 10)}.csv`;
      await exportSessionCsv(session.id, filename);
      toast({ title: s("Downloaded", "ڈاؤنلوڈ ہوگیا"), description: s(`"${session.title}" exported as CSV.`, `"${session.title}" CSV میں برآمد ہو گیا۔`) });
    } catch {
      toast({ title: s("Error", "خرابی"), description: s("Could not export session.", "سیشن برآمد نہیں ہو سکا۔"), variant: "destructive" });
    } finally {
      setDownloading(false);
    }
  };

  const handleClearAll = async () => {
    if (!window.confirm(s("Delete ALL conversations permanently?", "تمام گفتگوئیں مستقل طور پر حذف کریں؟"))) return;
    setClearing(true);
    try {
      await deleteAllSessions();
      setSessions([]);
      toast({ title: s("Chats cleared", "گفتگو صاف ہو گئی"), description: s("All conversations deleted.", "تمام گفتگوئیں حذف ہو گئیں۔") });
    } catch {
      toast({ title: s("Error", "خرابی"), description: s("Could not clear chats.", "گفتگو صاف نہیں ہو سکی۔"), variant: "destructive" });
    } finally {
      setClearing(false);
    }
  };

  return (
    <>
      <Section
        title={s("Chat", "گفتگو")}
        desc={s("Export and manage your conversation history.", "اپنی گفتگو کی تاریخ برآمد اور منظم کریں۔")}
      >
        <Row
          icon={FileText}
          title={s("Export session as CSV", "سیشن CSV کے طور پر برآمد کریں")}
          desc={s("Search and pick a session to download.", "ڈاؤنلوڈ کے لیے سیشن تلاش کریں۔")}
        >
          <Button
            variant="outline"
            size="sm"
            className="text-foreground gap-1"
            onClick={() => setShowPicker(true)}
            disabled={downloading || sessions.length === 0}
          >
            <Download className="w-4 h-4" />
            {downloading ? s("Exporting…", "برآمد ہو رہا ہے…") : s("Download CSV", "CSV ڈاؤنلوڈ")}
          </Button>
        </Row>

        <Row
          icon={Trash2}
          title={s("Clear all chats", "تمام گفتگو صاف کریں")}
          desc={s("Permanently delete all your conversation sessions.", "اپنی تمام گفتگو کی تاریخ ہمیشہ کے لیے حذف کریں۔")}
        >
          <Button variant="destructive" size="sm" onClick={handleClearAll} disabled={clearing}>
            {clearing ? "..." : s("Clear all", "سب صاف کریں")}
          </Button>
        </Row>
      </Section>

      {showPicker && (
        <SessionPickerModal
          sessions={sessions}
          onSelect={handleSelect}
          onClose={() => setShowPicker(false)}
          isUrdu={isUrdu}
        />
      )}
    </>
  );
};

export default Chat;
