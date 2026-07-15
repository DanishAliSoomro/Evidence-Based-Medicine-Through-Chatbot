import { NavLink, Outlet, useNavigate } from "react-router-dom";
import { Palette, MessageSquare, UserCircle2, ArrowLeft } from "lucide-react";
import SparkleIcon from "@/components/SparkleIcon";
import { useDarkMode } from "@/hooks/use-dark-mode";
import { useLanguage } from "@/hooks/use-language";

const sections = [
  { path: "general",     label: "General",        labelUr: "عمومی",              icon: Palette },
  { path: "chat",        label: "Chat",            labelUr: "گفتگو",              icon: MessageSquare },
  { path: "account",     label: "Account",         labelUr: "اکاؤنٹ",             icon: UserCircle2 },
];

const Settings = () => {
  const navigate = useNavigate();
  const [darkMode] = useDarkMode();
  const [language] = useLanguage();
  const isUrdu = language === "ur";
  const s = (en, ur) => (isUrdu ? ur : en);

  return (
    <div className={`min-h-screen flex bg-background ${darkMode ? "dark" : ""}`} dir={isUrdu ? "rtl" : "ltr"}>
      {/* Desktop sidebar */}
      <div className="hidden lg:flex lg:w-80 bg-gradient-to-br from-[hsl(217,50%,15%)] via-[hsl(217,45%,20%)] to-[hsl(217,40%,12%)] relative overflow-hidden flex-col">
        <div className="absolute top-1/4 -left-20 w-80 h-80 bg-emerald-500/30 rounded-full blur-3xl" />
        <div className="absolute bottom-1/4 right-10 w-60 h-60 bg-emerald-500/20 rounded-full blur-3xl" />
        <div className="relative z-10 p-8 flex flex-col h-full">
          <div className="flex items-center gap-3 mb-10">
            <div className="w-12 h-12 rounded-xl bg-emerald-500 flex items-center justify-center">
              <SparkleIcon className="w-7 h-7 text-white" />
            </div>
            <span className="text-2xl font-bold text-white">EBM AI</span>
          </div>
          <h1 className="text-3xl font-bold text-white mb-3">{s("Settings", "ترتیبات")}</h1>
          <p className="text-white/70 mb-8">
            {s(
              "Customize your experience and manage your account preferences.",
              "اپنا تجربہ انداز کریں اور اکاؤنٹ ترجیحات سنبھالیں۔"
            )}
          </p>
          <nav className="space-y-1 flex-1">
            {sections.map((sec) => {
              const Icon = sec.icon;
              return (
                <NavLink
                  key={sec.path}
                  to={`/settings/${sec.path}`}
                  className={({ isActive }) =>
                    `w-full flex items-center gap-3 px-4 py-3 rounded-lg transition-colors ${
                      isActive ? "bg-emerald-500 text-white" : "text-white/80 hover:bg-white/10"
                    }`
                  }
                >
                  <Icon className="w-5 h-5" />
                  <span className="font-medium">{isUrdu ? sec.labelUr : sec.label}</span>
                </NavLink>
              );
            })}
          </nav>
          <button
            onClick={() => navigate("/")}
            className="flex items-center gap-2 text-white/70 hover:text-white transition-colors mt-6"
          >
            <ArrowLeft className="w-4 h-4" />
            {s("Back to chat", "گفتگو پر واپس جائیں")}
          </button>
        </div>
      </div>

      {/* Content area */}
      <div className="flex-1 overflow-y-auto">
        <div className="max-w-2xl mx-auto p-8 lg:p-12">
          {/* Mobile tabs */}
          <div className="lg:hidden flex gap-2 overflow-x-auto pb-4 mb-6">
            {sections.map((sec) => (
              <NavLink
                key={sec.path}
                to={`/settings/${sec.path}`}
                className={({ isActive }) =>
                  `px-4 py-2 rounded-lg text-sm whitespace-nowrap ${
                    isActive ? "bg-primary text-primary-foreground" : "bg-card text-foreground"
                  }`
                }
              >
                {isUrdu ? sec.labelUr : sec.label}
              </NavLink>
            ))}
          </div>

          <Outlet />
        </div>
      </div>
    </div>
  );
};

export default Settings;
