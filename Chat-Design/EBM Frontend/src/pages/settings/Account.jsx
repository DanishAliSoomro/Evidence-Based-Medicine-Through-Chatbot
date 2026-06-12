import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { UserCircle2, Mail, AlertTriangle } from "lucide-react";
import { useLanguage } from "@/hooks/use-language";
import { toast } from "@/hooks/use-toast";
import { Section, Button, Input, DeleteDialog } from "./SettingsShared";

const Account = () => {
  const navigate = useNavigate();
  const [language] = useLanguage();
  const isUrdu = language === "ur";
  const s = (en, ur) => (isUrdu ? ur : en);

  const [username, setUsername] = useState(
    () => localStorage.getItem("ebm-username") || "Dr. Researcher"
  );
  const [userEmail] = useState(
    () => localStorage.getItem("ebm-email") || "user@gmail.com"
  );
  const [editingName, setEditingName] = useState(false);
  const [draftName, setDraftName] = useState(username);
  const [showDeleteDialog, setShowDeleteDialog] = useState(false);

  const saveUsername = () => {
    const name = draftName.trim() || username;
    setUsername(name);
    localStorage.setItem("ebm-username", name);
    setEditingName(false);
    toast({ title: s("Username updated", "صارف نام اپڈیٹ ہو گیا") });
  };

  const handleDeleteAccount = () => {
    setShowDeleteDialog(false);
    localStorage.clear();
    toast({
      title: s("Account deleted", "اکاؤنٹ حذف ہو گیا"),
      description: s("Your account has been removed.", "آپ کا اکاؤنٹ ہٹا دیا گیا ہے۔"),
      variant: "destructive",
    });
    navigate("/login");
  };

  return (
    <>
      <Section
        title={s("Account", "اکاؤنٹ")}
        desc={s(
          "Manage your personal information and account settings.",
          "اپنی ذاتی معلومات اور اکاؤنٹ ترتیبات سنبھالیں۔"
        )}
      >
        {/* Username */}
        <div className="p-5 rounded-xl bg-card border border-border space-y-3">
          <label className="flex items-center gap-2 text-sm font-medium text-foreground">
            <UserCircle2 className="w-4 h-4 text-primary" />
            {s("Username", "صارف نام")}
          </label>
          {editingName ? (
            <div className="flex gap-2">
              <Input
                value={draftName}
                onChange={(e) => setDraftName(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && saveUsername()}
                className="h-10 bg-background text-foreground"
                autoFocus
              />
              <Button size="sm" onClick={saveUsername}>
                {s("Save", "محفوظ کریں")}
              </Button>
              <Button
                size="sm"
                variant="outline"
                onClick={() => { setEditingName(false); setDraftName(username); }}
              >
                {s("Cancel", "رد کریں")}
              </Button>
            </div>
          ) : (
            <div className="flex items-center justify-between">
              <span className="text-foreground font-medium">{username}</span>
              <Button
                size="sm"
                variant="outline"
                onClick={() => { setDraftName(username); setEditingName(true); }}
              >
                {s("Change", "تبدیل کریں")}
              </Button>
            </div>
          )}
        </div>

        {/* Email */}
        <div className="p-5 rounded-xl bg-card border border-border space-y-3">
          <label className="flex items-center gap-2 text-sm font-medium text-foreground">
            <Mail className="w-4 h-4 text-primary" />
            {s("Email address", "ایمیل پتہ")}
          </label>
          <div className="flex items-center justify-between">
            <span className="text-foreground font-medium">{userEmail}</span>
            <span className="text-xs text-muted-foreground bg-muted px-2 py-1 rounded-full">
              {s("Read-only", "صرف پڑھنے کے لیے")}
            </span>
          </div>
          <p className="text-xs text-muted-foreground">
            {s(
              "Your email address cannot be changed after registration.",
              "رجسٹریشن کے بعد آپ کا ایمیل پتہ تبدیل نہیں کیا جا سکتا۔"
            )}
          </p>
        </div>

        {/* Delete account */}
        <div className="p-5 rounded-xl bg-destructive/5 border border-destructive/30 space-y-3">
          <div className="flex items-start gap-3">
            <div className="w-10 h-10 rounded-lg bg-destructive/10 flex items-center justify-center flex-shrink-0">
              <AlertTriangle className="w-5 h-5 text-destructive" />
            </div>
            <div className="min-w-0">
              <p className="font-medium text-foreground">{s("Delete account", "اکاؤنٹ حذف کریں")}</p>
              <p className="text-sm text-muted-foreground">
                {s(
                  "Permanently remove your account and all associated data. This action cannot be undone.",
                  "اپنا اکاؤنٹ اور تمام منسلک ڈیٹا ہمیشہ کے لیے حذف کریں۔"
                )}
              </p>
            </div>
          </div>
          <div className="flex justify-end">
            <Button variant="destructive" size="sm" onClick={() => setShowDeleteDialog(true)}>
              {s("Delete my account", "میرا اکاؤنٹ حذف کریں")}
            </Button>
          </div>
        </div>
      </Section>

      {showDeleteDialog && (
        <DeleteDialog
          onConfirm={handleDeleteAccount}
          onCancel={() => setShowDeleteDialog(false)}
          isUrdu={isUrdu}
        />
      )}
    </>
  );
};

export default Account;
