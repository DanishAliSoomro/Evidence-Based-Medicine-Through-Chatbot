import { useState } from "react";
import { KeyRound, Check } from "lucide-react";
import { useLanguage } from "@/hooks/use-language";
import { toast } from "@/hooks/use-toast";
import { Section, Button, Input } from "./SettingsShared";

const STORAGE_KEY = "ebm-api-key";

const DataControl = () => {
  const [language] = useLanguage();
  const [apiKey, setApiKey] = useState(() => localStorage.getItem(STORAGE_KEY) || "");
  const [saved, setSaved] = useState(false);
  const isUrdu = language === "ur";
  const s = (en, ur) => (isUrdu ? ur : en);

  const saveApiKey = () => {
    localStorage.setItem(STORAGE_KEY, apiKey.trim());
    setSaved(true);
    toast({
      title: s("API key saved", "API کی محفوظ ہو گئی"),
      description: s("Stored locally on this device.", "آلہ پر محفوظ ہے۔"),
    });
    setTimeout(() => setSaved(false), 2000);
  };

  return (
    <Section
      title={s("Data Controls", "ڈیٹا کنٹرولز")}
      desc={s(
        "Bring your own AI model API key. Stored locally on this device.",
        "اپنی AI ماڈل API کی لائیں۔ یہ آلہ پر محفوظ ہے۔"
      )}
    >
      <div className="p-5 rounded-xl bg-card border border-border space-y-4">
        <label className="flex items-center gap-2 text-sm font-medium text-foreground">
          <KeyRound className="w-4 h-4 text-primary" />
          {s("API Key", "API کی")}
        </label>
        <Input
          type="password"
          value={apiKey}
          onChange={(e) => setApiKey(e.target.value)}
          placeholder={s("Paste any API key...", "کوئی بھی API کی یہاں لگائیں...")}
          className="h-12 bg-background text-foreground font-mono text-sm"
        />
        <div className="flex justify-end">
          <Button onClick={saveApiKey} disabled={!apiKey.trim()} className="min-w-[80px]">
            {saved ? <Check className="w-4 h-4" /> : s("Save", "محفوظ کریں")}
          </Button>
        </div>
      </div>

      <div className="p-4 rounded-xl bg-primary/5 border border-primary/20 text-sm text-muted-foreground">
        {s(
          "Your key is never sent to our servers. It is saved only in your browser local storage and used directly for API calls.",
          "آپ کی کی ہمارے سرور نہیں بھیجی جاتی۔ یہ صرف براؤزر میں ذخیرہ ہوتی ہے۔"
        )}
      </div>
    </Section>
  );
};

export default DataControl;
