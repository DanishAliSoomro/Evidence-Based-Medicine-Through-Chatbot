import * as React from "react";
import { useNavigate } from "react-router-dom";
import * as DropdownMenuPrimitive from "@radix-ui/react-dropdown-menu";
import { Slot } from "@radix-ui/react-slot";
import { cva } from "class-variance-authority";
import { Plus, User, Settings, Users, PanelLeftClose, LogOut } from "lucide-react";
import { cn } from "@/lib/utils";
import { useAuth } from "@/hooks/use-auth";
import { useLanguage } from "@/hooks/use-language";
import ConversationList from "./ConversationList";

const s = (lang, en, ur) => (lang === "ur" ? ur : en);

/* ---------- DropdownMenu (for user account footer only) ---------- */
const DropdownMenu = DropdownMenuPrimitive.Root;
const DropdownMenuTrigger = DropdownMenuPrimitive.Trigger;
const DropdownMenuContent = React.forwardRef(({ className, sideOffset = 4, ...props }, ref) => (
  <DropdownMenuPrimitive.Portal>
    <DropdownMenuPrimitive.Content
      ref={ref}
      sideOffset={sideOffset}
      className={cn(
        "z-50 min-w-[8rem] overflow-hidden rounded-md border bg-popover p-1 text-popover-foreground shadow-md data-[state=open]:animate-in data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0 data-[state=closed]:zoom-out-95 data-[state=open]:zoom-in-95",
        className,
      )}
      {...props}
    />
  </DropdownMenuPrimitive.Portal>
));
const DropdownMenuItem = React.forwardRef(({ className, ...props }, ref) => (
  <DropdownMenuPrimitive.Item
    ref={ref}
    className={cn(
      "relative flex cursor-default select-none items-center rounded-sm px-2 py-1.5 text-sm outline-none transition-colors data-[disabled]:pointer-events-none data-[disabled]:opacity-50 focus:bg-accent focus:text-accent-foreground",
      className,
    )}
    {...props}
  />
));
const DropdownMenuSeparator = React.forwardRef(({ className, ...props }, ref) => (
  <DropdownMenuPrimitive.Separator ref={ref} className={cn("-mx-1 my-1 h-px bg-muted", className)} {...props} />
));

/* =================================================================
   ChatSidebar
   Owns the sidebar shell only:
     - header (title + close button)
     - New Chat button
     - <ConversationList /> — self-contained: search, list, share dialog
     - user account footer dropdown
   ================================================================= */
const ChatSidebar = ({
  onNewChat,
  conversations,
  onSelectChat,
  onDeleteChat,
  activeChat,
  onClose,
  currentUser,
}) => {
  const navigate = useNavigate();
  const { logout } = useAuth();
  const [lang] = useLanguage();

  return (
    <aside className="w-64 h-screen bg-sidebar flex flex-col">
      {/* Header */}
      <div className="p-3 flex items-center justify-between border-b border-sidebar-border">
        <span className="font-semibold text-sidebar-foreground">{s(lang, "Chats", "چیٹس")}</span>
        <button
          onClick={onClose}
          className="p-1.5 rounded-md hover:bg-sidebar-accent text-sidebar-foreground/70 hover:text-sidebar-foreground transition-colors"
          title="Close sidebar"
        >
          <PanelLeftClose className="w-5 h-5" />
        </button>
      </div>

      {/* New chat button */}
      <div className="p-3 pb-1">
        <button onClick={onNewChat} className="sidebar-item sidebar-item-active w-full">
          <Plus className="w-5 h-5" />
          <span className="font-medium">{s(lang, "New chat", "نئی چیٹ")}</span>
        </button>
      </div>

      {/* Conversation list — manages search, rows, share dialog internally */}
      <ConversationList
        conversations={conversations}
        activeChat={activeChat}
        onSelectChat={onSelectChat}
        onDeleteChat={onDeleteChat}
      />

      {/* User account footer */}
      <div className="p-3 border-t border-sidebar-border">
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <button className="sidebar-item w-full">
              <div className="w-8 h-8 rounded-full bg-sidebar-accent flex items-center justify-center">
                <User className="w-4 h-4 text-sidebar-foreground" />
              </div>
              <span className="truncate">{currentUser?.username || "Account"}</span>
            </button>
          </DropdownMenuTrigger>
          <DropdownMenuContent side="top" align="start" className="w-64 bg-popover border border-border">
            <div className="px-2 py-2">
              <p className="text-sm font-medium text-foreground">
                {currentUser?.username || "Your Name"}
              </p>
              <p className="text-xs text-muted-foreground">
                {currentUser?.email || "—"}
              </p>
            </div>
            <DropdownMenuSeparator />
            <DropdownMenuItem
              onClick={() => navigate("/settings")}
              className="flex items-center gap-2 cursor-pointer"
            >
              <Settings className="w-4 h-4" />
              <span>{s(lang, "Settings", "ترتیبات")}</span>
            </DropdownMenuItem>
            <DropdownMenuItem
              onClick={() => navigate("/settings/account")}
              className="flex items-center gap-2 cursor-pointer"
            >
              <Users className="w-4 h-4" />
              <span>{s(lang, "Accounts", "اکاؤنٹس")}</span>
            </DropdownMenuItem>
            <DropdownMenuSeparator />
            <DropdownMenuItem
              onClick={() => { logout(); navigate("/login"); }}
              className="flex items-center gap-2 cursor-pointer text-destructive focus:text-destructive"
            >
              <LogOut className="w-4 h-4" />
              <span>{s(lang, "Log out", "لاگ آؤٹ")}</span>
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>
    </aside>
  );
};

export default ChatSidebar;
