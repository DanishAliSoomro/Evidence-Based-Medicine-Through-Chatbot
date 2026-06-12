import { useState } from "react";
import { Download, Trash2 } from "lucide-react";
import { useLanguage } from "@/hooks/use-language";
import { toast } from "@/hooks/use-toast";
import { exportAllSessions, deleteAllSessions } from "@/api/chatApi";
import { Section, Row, Button } from "./SettingsShared";

const Chat = () => {
  const [language] = useLanguage();
  const [clearing, setClearing] = useState(false);
  const isUrdu = language === "ur";
  const s = (en, ur) => (isUrdu ? ur : en);

  const handleExport = async () => {
    try {
      const data = await exportAllSessions();
      const blob = new Blob([JSON.stringify(data, null, 2)], { type: "application/json" });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `ebm-chats-${new Date().toISOString().slice(0, 10)}.json`;
      a.click();
      URL.revokeObjectURL(url);
      toast({ title: s("Exported", "برآمد"), description: s("Chats downloaded as JSON.", "گفتگو JSON میں ڈاؤنلوڈ ہو گئی۔") });
    } catch {
      toast({ title: s("Error", "خرابی"), description: s("Could not export chats.", "گفتگو برآمد نہیں ہو سکی۔"), variant: "destructive" });
    }
  };

  const handleClear = async () => {
    if (!window.confirm(s("Delete ALL conversations permanently?", "تمام گفتگوئیں مستقل طور پر حذف کریں؟"))) return;
    setClearing(true);
    try {
      await deleteAllSessions();
      toast({ title: s("Chats cleared", "گفتگو صاف ہو گئی"), description: s("All conversations deleted.", "تمام گفتگوئیں حذف ہو گئیں۔") });
    } catch {
      toast({ title: s("Error", "خرابی"), description: s("Could not clear chats.", "گفتگو صاف نہیں ہو سکی۔"), variant: "destructive" });
    } finally {
      setClearing(false);
    }
  };

  return (
    <Section
      title={s("Chat", "گفتگو")}
      desc={s(
        "Export and manage your conversation history.",
        "اپنی گفتگو کی تاریخ برآمد اور منظم کریں۔"
      )}
    >
      <Row
        icon={Download}
        title={s("Export chats", "گفتگو برآمد کریں")}
        desc={s("Download all conversations as JSON.", "تمام باتچیتیں JSON میں ڈاؤنلوڈ کریں۔")}
      >
        <Button variant="outline" size="sm" className="text-foreground" onClick={handleExport}>
          {s("Export", "برآمد")}
        </Button>
      </Row>

      <Row
        icon={Trash2}
        title={s("Clear all chats", "تمام گفتگو صاف کریں")}
        desc={s("Permanently delete all conversation history.", "ساری گفتگو کی تاریخ ہمیشہ کے لیے حذف کریں۔")}
      >
        <Button variant="destructive" size="sm" onClick={handleClear} disabled={clearing}>
          {clearing ? "..." : s("Clear", "صاف کریں")}
        </Button>
      </Row>
    </Section>
  );
};

export default Chat;
