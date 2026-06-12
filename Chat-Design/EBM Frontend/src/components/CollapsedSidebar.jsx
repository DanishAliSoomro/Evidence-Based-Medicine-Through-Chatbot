import * as React from "react";
import * as DropdownMenuPrimitive from "@radix-ui/react-dropdown-menu";
import { PanelLeft, Plus, Search, MessageSquare, User, Settings, Users, Trash2 } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { cn } from "@/lib/utils";
import { toast } from "@/hooks/use-toast";

/* ---------- Inline DropdownMenu ---------- */
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

const CollapsedSidebar = ({ onOpenSidebar, onNewChat, onSearchChats }) => {
  const navigate = useNavigate();
  const railBtn =
    "p-2 rounded-md text-sidebar-foreground/80 hover:text-sidebar-foreground hover:bg-sidebar-accent transition-colors";
  return (
    <aside className="w-14 h-screen bg-sidebar flex flex-col items-center justify-between py-3">
      <div className="flex flex-col items-center gap-2">
        <button onClick={onOpenSidebar} className={railBtn} title="Open sidebar">
          <PanelLeft className="w-5 h-5" />
        </button>
        <button onClick={onNewChat} className={railBtn} title="New chat">
          <Plus className="w-5 h-5" />
        </button>
        <button onClick={onSearchChats} className={railBtn} title="Search chats">
          <Search className="w-5 h-5" />
        </button>
        <button onClick={onOpenSidebar} className={railBtn} title="Chats">
          <MessageSquare className="w-5 h-5" />
        </button>
      </div>

      <DropdownMenu>
        <DropdownMenuTrigger asChild>
          <button
            className="w-8 h-8 rounded-full bg-sidebar-accent flex items-center justify-center text-sidebar-foreground hover:bg-sidebar-accent/80 transition-colors"
            title="Account"
          >
            <User className="w-4 h-4" />
          </button>
        </DropdownMenuTrigger>
        <DropdownMenuContent side="top" align="start" className="w-64 bg-popover border border-border">
          <div className="px-2 py-2">
            <p className="text-sm font-medium text-foreground">Your Name</p>
            <p className="text-xs text-muted-foreground">your.email@example.com</p>
          </div>
          <DropdownMenuSeparator />
          <DropdownMenuItem onClick={() => navigate("/settings")} className="flex items-center gap-2 cursor-pointer">
            <Settings className="w-4 h-4" />
            <span>Settings</span>
          </DropdownMenuItem>
          <DropdownMenuItem className="flex items-center gap-2 cursor-pointer">
            <Users className="w-4 h-4" />
            <span>Accounts</span>
          </DropdownMenuItem>
          <DropdownMenuSeparator />
          <DropdownMenuItem
            onClick={() =>
              toast({ title: "Account deletion", description: "This will permanently delete your account." })
            }
            className="flex items-center gap-2 cursor-pointer text-destructive focus:text-destructive"
          >
            <Trash2 className="w-4 h-4" />
            <span>Delete account</span>
          </DropdownMenuItem>
        </DropdownMenuContent>
      </DropdownMenu>
    </aside>
  );
};

export default CollapsedSidebar;